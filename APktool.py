#!/usr/bin/env python3
"""
Apktool MCP Server
A Model Context Protocol server that exposes Apktool functionality for Android APK analysis and modification.
Integrates with Gemini CLI for AI-powered APK reverse engineering workflows.
"""

import asyncio
import json
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    Resource,
    Prompt,
    GetPromptResult,
    CallToolResult,
    ListResourcesResult,
    ListPromptsResult,
    ListToolsResult,
    ReadResourceResult,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("apktool-mcp")

class ApktoolMCPServer:
    def __init__(self, apktool_path: str = "apktool", work_dir: str = None):
        """
        Initialize the Apktool MCP Server
        
        Args:
            apktool_path: Path to apktool executable (default: "apktool")
            work_dir: Working directory for APK operations (default: temp dir)
        """
        self.apktool_path = apktool_path
        self.work_dir = Path(work_dir) if work_dir else Path(tempfile.mkdtemp())
        self.work_dir.mkdir(exist_ok=True)
        
        # Initialize MCP server
        self.server = Server("apktool-mcp")
        self._setup_tools()
        self._setup_resources()
        self._setup_prompts()
        
    def _setup_tools(self):
        """Register all available tools with the MCP server"""
        
        @self.server.list_tools()
        async def list_tools() -> ListToolsResult:
            return ListToolsResult(
                tools=[
                    Tool(
                        name="decode_apk",
                        description="Decompile an APK file to extract resources, manifest, and smali code",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "apk_path": {"type": "string", "description": "Path to the APK file"},
                                "output_dir": {"type": "string", "description": "Output directory name (optional)"},
                                "force": {"type": "boolean", "description": "Force overwrite existing directory", "default": False},
                                "no_res": {"type": "boolean", "description": "Do not decode resources", "default": False},
                                "no_src": {"type": "boolean", "description": "Do not decode sources", "default": False}
                            },
                            "required": ["apk_path"]
                        }
                    ),
                    Tool(
                        name="build_apk",
                        description="Recompile/build an APK from decompiled source directory",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "source_dir": {"type": "string", "description": "Path to decompiled APK directory"},
                                "output_apk": {"type": "string", "description": "Output APK filename (optional)"},
                                "force": {"type": "boolean", "description": "Force build all files", "default": False}
                            },
                            "required": ["source_dir"]
                        }
                    ),
                    Tool(
                        name="install_framework",
                        description="Install framework APK for system app decompilation",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "framework_path": {"type": "string", "description": "Path to framework APK file"},
                                "tag": {"type": "string", "description": "Tag for framework identification (optional)"}
                            },
                            "required": ["framework_path"]
                        }
                    ),
                    Tool(
                        name="analyze_manifest",
                        description="Analyze AndroidManifest.xml from a decompiled APK",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "apk_dir": {"type": "string", "description": "Path to decompiled APK directory"}
                            },
                            "required": ["apk_dir"]
                        }
                    ),
                    Tool(
                        name="extract_strings",
                        description="Extract all string resources from a decompiled APK",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "apk_dir": {"type": "string", "description": "Path to decompiled APK directory"},
                                "locale": {"type": "string", "description": "Specific locale (e.g., 'en', 'es')", "default": ""}
                            },
                            "required": ["apk_dir"]
                        }
                    ),
                    Tool(
                        name="list_permissions",
                        description="List all permissions requested by an APK",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "apk_dir": {"type": "string", "description": "Path to decompiled APK directory"}
                            },
                            "required": ["apk_dir"]
                        }
                    ),
                    Tool(
                        name="find_smali_references",
                        description="Search for specific patterns in smali code",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "apk_dir": {"type": "string", "description": "Path to decompiled APK directory"},
                                "pattern": {"type": "string", "description": "Search pattern or string"},
                                "case_sensitive": {"type": "boolean", "description": "Case sensitive search", "default": True}
                            },
                            "required": ["apk_dir", "pattern"]
                        }
                    ),
                    Tool(
                        name="get_apk_info",
                        description="Get basic information about an APK file using aapt",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "apk_path": {"type": "string", "description": "Path to the APK file"}
                            },
                            "required": ["apk_path"]
                        }
                    )
                ]
            )

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            try:
                if name == "decode_apk":
                    result = await self._decode_apk(**arguments)
                elif name == "build_apk":
                    result = await self._build_apk(**arguments)
                elif name == "install_framework":
                    result = await self._install_framework(**arguments)
                elif name == "analyze_manifest":
                    result = await self._analyze_manifest(**arguments)
                elif name == "extract_strings":
                    result = await self._extract_strings(**arguments)
                elif name == "list_permissions":
                    result = await self._list_permissions(**arguments)
                elif name == "find_smali_references":
                    result = await self._find_smali_references(**arguments)
                elif name == "get_apk_info":
                    result = await self._get_apk_info(**arguments)
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return CallToolResult(content=[TextContent(type="text", text=result)])
                
            except Exception as e:
                error_msg = f"Error executing {name}: {str(e)}"
                logger.error(error_msg)
                return CallToolResult(content=[TextContent(type="text", text=error_msg)], isError=True)

    def _setup_resources(self):
        """Setup resources for accessing decompiled APK data"""
        
        @self.server.list_resources()
        async def list_resources() -> ListResourcesResult:
            resources = []
            
            # List all decompiled APK directories
            for item in self.work_dir.iterdir():
                if item.is_dir():
                    resources.append(
                        Resource(
                            uri=f"apktool://apk/{item.name}/manifest",
                            name=f"{item.name} - AndroidManifest.xml",
                            mimeType="application/xml"
                        )
                    )
                    resources.append(
                        Resource(
                            uri=f"apktool://apk/{item.name}/apktool_yml",
                            name=f"{item.name} - apktool.yml",
                            mimeType="application/yaml"
                        )
                    )
            
            return ListResourcesResult(resources=resources)

        @self.server.read_resource()
        async def read_resource(uri: str) -> ReadResourceResult:
            try:
                if uri.startswith("apktool://apk/"):
                    parts = uri.split("/")
                    apk_name = parts[3]
                    resource_type = parts[4]
                    
                    apk_dir = self.work_dir / apk_name
                    
                    if resource_type == "manifest":
                        manifest_path = apk_dir / "AndroidManifest.xml"
                        if manifest_path.exists():
                            content = manifest_path.read_text(encoding='utf-8')
                            return ReadResourceResult(contents=[TextContent(type="text", text=content)])
                    
                    elif resource_type == "apktool_yml":
                        yml_path = apk_dir / "apktool.yml"
                        if yml_path.exists():
                            content = yml_path.read_text(encoding='utf-8')
                            return ReadResourceResult(contents=[TextContent(type="text", text=content)])
                
                raise FileNotFoundError(f"Resource not found: {uri}")
                
            except Exception as e:
                error_msg = f"Error reading resource {uri}: {str(e)}"
                return ReadResourceResult(contents=[TextContent(type="text", text=error_msg)])

    def _setup_prompts(self):
        """Setup prompts for common APK analysis tasks"""
        
        @self.server.list_prompts()
        async def list_prompts() -> ListPromptsResult:
            return ListPromptsResult(
                prompts=[
                    Prompt(
                        name="analyze_security",
                        description="Analyze APK for potential security issues",
                        arguments=[
                            {"name": "apk_path", "description": "Path to APK file", "required": True}
                        ]
                    ),
                    Prompt(
                        name="privacy_audit",
                        description="Audit APK for privacy-related permissions and data collection",
                        arguments=[
                            {"name": "apk_path", "description": "Path to APK file", "required": True}
                        ]
                    ),
                    Prompt(
                        name="reverse_engineer_guide",
                        description="Step-by-step guide for reverse engineering an APK",
                        arguments=[
                            {"name": "apk_path", "description": "Path to APK file", "required": True},
                            {"name": "target_feature", "description": "Specific feature to analyze", "required": False}
                        ]
                    )
                ]
            )

        @self.server.get_prompt()
        async def get_prompt(name: str, arguments: Dict[str, str]) -> GetPromptResult:
            if name == "analyze_security":
                apk_path = arguments.get("apk_path", "")
                prompt_text = f"""
Please perform a comprehensive security analysis of the APK file: {apk_path}

Steps to follow:
1. Use decode_apk to decompile the APK
2. Use analyze_manifest to examine permissions and components
3. Use list_permissions to identify potentially dangerous permissions
4. Use find_smali_references to search for:
   - Crypto/encryption usage
   - Network communications
   - File I/O operations
   - Sensitive API calls
5. Look for hardcoded secrets, API keys, or credentials
6. Analyze app components for potential vulnerabilities

Provide a detailed security assessment with:
- Risk level (Low/Medium/High)
- Identified vulnerabilities
- Recommendations for mitigation
"""
                
            elif name == "privacy_audit":
                apk_path = arguments.get("apk_path", "")
                prompt_text = f"""
Conduct a privacy audit for the APK file: {apk_path}

Analysis should include:
1. Decompile the APK using decode_apk
2. Extract and analyze all permissions with list_permissions
3. Identify data collection patterns in smali code
4. Check for third-party SDK integrations
5. Examine network communications and endpoints
6. Review privacy policy compliance indicators

Generate a privacy report covering:
- Personal data types collected
- Data sharing with third parties
- User consent mechanisms
- Compliance with privacy regulations (GDPR, CCPA)
"""
                
            elif name == "reverse_engineer_guide":
                apk_path = arguments.get("apk_path", "")
                target_feature = arguments.get("target_feature", "general functionality")
                prompt_text = f"""
Create a reverse engineering guide for APK: {apk_path}
Target analysis: {target_feature}

Provide step-by-step instructions for:
1. Initial APK decompilation and structure analysis
2. Understanding the app architecture from AndroidManifest.xml
3. Identifying key components and entry points
4. Analyzing smali code for the target feature
5. Resource analysis (strings, layouts, assets)
6. Modification strategies if needed
7. Recompilation and testing approaches

Include specific apktool commands and file locations to examine.
"""
            
            else:
                prompt_text = f"Unknown prompt: {name}"
            
            return GetPromptResult(
                description=f"APK analysis prompt for {name}",
                messages=[
                    {
                        "role": "user",
                        "content": {
                            "type": "text",
                            "text": prompt_text
                        }
                    }
                ]
            )

    async def _run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> str:
        """Execute a command and return its output"""
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd or self.work_dir
            )
            stdout, stderr = await process.communicate()
            
            output = stdout.decode('utf-8', errors='ignore')
            error = stderr.decode('utf-8', errors='ignore')
            
            if process.returncode != 0:
                raise RuntimeError(f"Command failed: {' '.join(cmd)}\nError: {error}")
            
            return output if output else error
            
        except Exception as e:
            raise RuntimeError(f"Failed to execute command: {' '.join(cmd)}\nError: {str(e)}")

    async def _decode_apk(self, apk_path: str, output_dir: str = None, 
                         force: bool = False, no_res: bool = False, 
                         no_src: bool = False) -> str:
        """Decompile an APK file using apktool"""
        apk_file = Path(apk_path)
        if not apk_file.exists():
            raise FileNotFoundError(f"APK file not found: {apk_path}")
        
        if not output_dir:
            output_dir = apk_file.stem
        
        output_path = self.work_dir / output_dir
        
        cmd = [self.apktool_path, "d", str(apk_file)]
        
        if force:
            cmd.append("-f")
        if no_res:
            cmd.append("-r")
        if no_src:
            cmd.append("-s")
        
        cmd.extend(["-o", str(output_path)])
        
        result = await self._run_command(cmd)
        
        return f"Successfully decompiled APK to: {output_path}\n\nOutput:\n{result}"

    async def _build_apk(self, source_dir: str, output_apk: str = None, 
                        force: bool = False) -> str:
        """Build/recompile an APK from source directory"""
        source_path = Path(source_dir)
        if not source_path.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")
        
        cmd = [self.apktool_path, "b", str(source_path)]
        
        if force:
            cmd.append("-f")
        
        if output_apk:
            cmd.extend(["-o", output_apk])
        
        result = await self._run_command(cmd)
        
        return f"Successfully built APK from: {source_path}\n\nOutput:\n{result}"

    async def _install_framework(self, framework_path: str, tag: str = None) -> str:
        """Install framework APK for system app decompilation"""
        framework_file = Path(framework_path)
        if not framework_file.exists():
            raise FileNotFoundError(f"Framework file not found: {framework_path}")
        
        cmd = [self.apktool_path, "if", str(framework_file)]
        
        if tag:
            cmd.extend(["-t", tag])
        
        result = await self._run_command(cmd)
        
        return f"Successfully installed framework: {framework_path}\n\nOutput:\n{result}"

    async def _analyze_manifest(self, apk_dir: str) -> str:
        """Analyze AndroidManifest.xml from decompiled APK"""
        manifest_path = Path(apk_dir) / "AndroidManifest.xml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"AndroidManifest.xml not found in: {apk_dir}")
        
        content = manifest_path.read_text(encoding='utf-8')
        
        # Extract key information
        analysis = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if 'package=' in line:
                analysis.append(f"Package: {line}")
            elif 'android:name=' in line and 'activity' in line.lower():
                analysis.append(f"Activity: {line}")
            elif 'android:name=' in line and 'service' in line.lower():
                analysis.append(f"Service: {line}")
            elif 'android:name=' in line and 'receiver' in line.lower():
                analysis.append(f"Receiver: {line}")
            elif 'uses-permission' in line:
                analysis.append(f"Permission: {line}")
        
        analysis_text = '\n'.join(analysis) if analysis else "No key elements found"
        
        return f"AndroidManifest.xml Analysis:\n\n{analysis_text}\n\nFull content:\n{content}"

    async def _extract_strings(self, apk_dir: str, locale: str = "") -> str:
        """Extract string resources from decompiled APK"""
        res_dir = Path(apk_dir) / "res"
        if not res_dir.exists():
            raise FileNotFoundError(f"Resources directory not found: {res_dir}")
        
        strings_files = []
        if locale:
            strings_files = list(res_dir.glob(f"values-{locale}/strings.xml"))
        else:
            strings_files = list(res_dir.glob("values*/strings.xml"))
        
        if not strings_files:
            return f"No string files found for locale: {locale or 'default'}"
        
        all_strings = []
        for strings_file in strings_files:
            content = strings_file.read_text(encoding='utf-8')
            all_strings.append(f"\n--- {strings_file.name} ---\n{content}")
        
        return f"Extracted strings from {len(strings_files)} files:\n{''.join(all_strings)}"

    async def _list_permissions(self, apk_dir: str) -> str:
        """List all permissions from AndroidManifest.xml"""
        manifest_path = Path(apk_dir) / "AndroidManifest.xml"
        if not manifest_path.exists():
            raise FileNotFoundError(f"AndroidManifest.xml not found in: {apk_dir}")
        
        content = manifest_path.read_text(encoding='utf-8')
        permissions = []
        
        for line in content.split('\n'):
            if 'uses-permission' in line:
                permissions.append(line.strip())
        
        if not permissions:
            return "No permissions found in AndroidManifest.xml"
        
        return f"Found {len(permissions)} permissions:\n\n" + '\n'.join(permissions)

    async def _find_smali_references(self, apk_dir: str, pattern: str, 
                                   case_sensitive: bool = True) -> str:
        """Search for patterns in smali code"""
        smali_dirs = []
        apk_path = Path(apk_dir)
        
        # Find all smali directories
        for item in apk_path.iterdir():
            if item.is_dir() and item.name.startswith('smali'):
                smali_dirs.append(item)
        
        if not smali_dirs:
            return "No smali directories found"
        
        matches = []
        search_pattern = pattern if case_sensitive else pattern.lower()
        
        for smali_dir in smali_dirs:
            for smali_file in smali_dir.rglob("*.smali"):
                try:
                    content = smali_file.read_text(encoding='utf-8')
                    search_content = content if case_sensitive else content.lower()
                    
                    if search_pattern in search_content:
                        # Find line numbers
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            line_search = line if case_sensitive else line.lower()
                            if search_pattern in line_search:
                                matches.append(f"{smali_file.relative_to(apk_path)}:{i}: {line.strip()}")
                except Exception as e:
                    continue
        
        if not matches:
            return f"Pattern '{pattern}' not found in smali code"
        
        return f"Found {len(matches)} matches for '{pattern}':\n\n" + '\n'.join(matches[:50])

    async def _get_apk_info(self, apk_path: str) -> str:
        """Get basic APK information using aapt or alternative"""
        apk_file = Path(apk_path)
        if not apk_file.exists():
            raise FileNotFoundError(f"APK file not found: {apk_path}")
        
        try:
            # Try using aapt if available
            cmd = ["aapt", "dump", "badging", str(apk_file)]
            result = await self._run_command(cmd)
            return f"APK Information:\n\n{result}"
        except:
            # Fallback to basic file information
            stat = apk_file.stat()
            return f"APK File Information:\n" \
                   f"Path: {apk_file}\n" \
                   f"Size: {stat.st_size} bytes\n" \
                   f"Modified: {stat.st_mtime}\n" \
                   f"Note: aapt not available for detailed analysis"

    async def run(self, transport_type: str = "stdio"):
        """Run the MCP server"""
        if transport_type == "stdio":
            from mcp.server.stdio import stdio_server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream, 
                                    self.server.create_initialization_options())
        else:
            raise ValueError(f"Unsupported transport type: {transport_type}")

# Server instance
server_instance = None

async def main():
    """Main entry point for the MCP server"""
    import sys
    
    # Check if apktool is available
    try:
        process = await asyncio.create_subprocess_exec(
            "apktool", "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        if process.returncode != 0:
            raise FileNotFoundError()
    except:
        print("Warning: apktool not found in PATH. Please install apktool first.", file=sys.stderr)
        print("Visit: https://ibotpeaches.github.io/Apktool/install/", file=sys.stderr)
    
    # Create and run server
    global server_instance
    server_instance = ApktoolMCPServer()
    await server_instance.run()

if __name__ == "__main__":
    asyncio.run(main())