import { NextRequest, NextResponse } from "next/server";

interface MCPRequest {
  jsonrpc: "2.0";
  id: number | string;
  method: string;
  params?: any;
}

interface MCPResponse {
  jsonrpc: "2.0";
  id: number | string;
  result?: any;
  error?: {
    code: number;
    message: string;
    data?: any;
  };
}

interface CreateArtifactParams {
  path: string;
  data?: any;
  title?: string;
  actions?: any[];
}

// MCP Server for Neevs Artifacts
export async function POST(req: NextRequest) {
  try {
    const body: MCPRequest = await req.json();
    const { jsonrpc, id, method, params } = body;

    // Validate JSON-RPC 2.0 format
    if (jsonrpc !== "2.0") {
      return NextResponse.json({
        jsonrpc: "2.0",
        id: id || null,
        error: {
          code: -32600,
          message: "Invalid Request: jsonrpc must be '2.0'",
        },
      });
    }

    let response: MCPResponse;

    switch (method) {
      case "initialize":
        response = {
          jsonrpc: "2.0",
          id,
          result: {
            protocolVersion: "2024-11-05",
            capabilities: {
              tools: {},
            },
            serverInfo: {
              name: "neevs-artifacts-mcp-server",
              version: "1.0.0",
            },
          },
        };
        break;

      case "tools/list":
        response = {
          jsonrpc: "2.0",
          id,
          result: {
            tools: [
              {
                name: "create_artifact",
                description: `Create a new artifact tab using pre-loaded templates from artifacts.neevs.io.

Available templates:
- dashboard: Interactive charts and analytics dashboard (Chart.js + Tailwind)
- 3d: Three.js 3D visualization with OrbitControls
- editor: Monaco code editor with React
- forms: React Hook Form with Zod validation
- docs: Marked markdown renderer with Prism.js syntax highlighting

Example usage:
- Create an interactive sales dashboard with your data
- Visualize 3D models or data
- Open a code editor with pre-loaded content
- Generate forms with validation
- Display documentation with syntax highlighting

The template handles all heavy libraries - you just provide the data!`,
                inputSchema: {
                  type: "object",
                  properties: {
                    path: {
                      type: "string",
                      enum: ["dashboard", "3d", "editor", "forms", "docs"],
                      description: "Template type to use (e.g., 'dashboard', '3d', 'editor')",
                    },
                    data: {
                      type: "object",
                      description: "Data payload for the artifact (structure depends on template type)",
                    },
                    title: {
                      type: "string",
                      description: "Optional title for the tab (defaults to template name)",
                    },
                    actions: {
                      type: "array",
                      description: "Optional agent callback actions",
                      items: {
                        type: "object",
                        properties: {
                          name: {
                            type: "string",
                            description: "Action name",
                          },
                          description: {
                            type: "string",
                            description: "Action description",
                          },
                        },
                      },
                    },
                  },
                  required: ["path"],
                },
              },
            ],
          },
        };
        break;

      case "tools/call":
        const { name, arguments: toolArgs } = params;

        if (name === "create_artifact") {
          try {
            const result = await handleCreateArtifact(toolArgs as CreateArtifactParams);
            response = {
              jsonrpc: "2.0",
              id,
              result,
            };
          } catch (error: any) {
            response = {
              jsonrpc: "2.0",
              id,
              error: {
                code: -32000,
                message: error.message || "Failed to create artifact",
                data: error.data,
              },
            };
          }
        } else {
          response = {
            jsonrpc: "2.0",
            id,
            error: {
              code: -32601,
              message: `Unknown tool: ${name}`,
            },
          };
        }
        break;

      default:
        response = {
          jsonrpc: "2.0",
          id,
          error: {
            code: -32601,
            message: `Method not found: ${method}`,
          },
        };
    }

    return NextResponse.json(response);
  } catch (error: any) {
    return NextResponse.json({
      jsonrpc: "2.0",
      id: null,
      error: {
        code: -32700,
        message: "Parse error",
        data: error.message,
      },
    });
  }
}

// Handle OPTIONS for CORS
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}

async function handleCreateArtifact(params: CreateArtifactParams) {
  const { path, data = {}, title, actions = [] } = params;

  // Validate template path
  const validPaths = ["dashboard", "3d", "editor", "forms", "docs"];
  if (!validPaths.includes(path)) {
    throw new Error(`Invalid template path: ${path}. Must be one of: ${validPaths.join(", ")}`);
  }

  // Generate unique artifact ID
  const artifactId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

  // Construct artifact URL
  const artifactUrl = `https://artifacts.neevs.io/${path}`;

  // Prepare payload for injection
  const payload = {
    path,
    data,
    title: title || `${path.charAt(0).toUpperCase() + path.slice(1)} Artifact`,
    actions,
    artifactId,
  };

  return {
    content: [
      {
        type: "text",
        text: JSON.stringify(
          {
            success: true,
            message: `Created ${path} artifact`,
            artifactUrl,
            artifactId,
            payload,
            instructions: `Navigate to ${artifactUrl} and inject the payload using the browser extension.`,
          },
          null,
          2
        ),
      },
    ],
  };
}
