#!/usr/bin/env python3

from __future__ import annotations

from copy import deepcopy


def _ref(name: str) -> dict:
    return {"$ref": f"#/components/schemas/{name}"}


def _generic_object(description: str) -> dict:
    return {
        "type": "object",
        "description": description,
        "additionalProperties": True,
    }


def build_native_components() -> dict:
    return {
        "GoogleTimestamp": {
            "type": "string",
            "format": "date-time",
            "description": "RFC 3339 timestamp.",
        },
        "GoogleDuration": {
            "type": "string",
            "description": "Duration string ending in `s`, for example `3.5s`.",
        },
        "GoogleProtobufValue": {
            "description": "Conservative OpenAPI model for `google.protobuf.Value`.",
            "oneOf": [
                {"type": "string"},
                {"type": "number"},
                {"type": "boolean"},
                {
                    "type": "array",
                    "items": _ref("GoogleProtobufValue"),
                },
                {
                    "type": "object",
                    "additionalProperties": _ref("GoogleProtobufValue"),
                },
            ],
        },
        "Content": {
            "type": "object",
            "description": "Contains the multi-part content of a message.",
            "properties": {
                "parts": {
                    "type": "array",
                    "items": _ref("Part"),
                },
                "role": {
                    "type": "string",
                    "description": "Producer of the content. Common values are `user` and `model`.",
                },
            },
            "required": ["parts"],
            "additionalProperties": False,
        },
        "Part": {
            "type": "object",
            "description": "A single part of a multi-part message.",
            "properties": {
                "text": {"type": "string"},
                "inlineData": _ref("Blob"),
                "fileData": _ref("FileData"),
                "functionCall": _ref("FunctionCall"),
                "functionResponse": _ref("FunctionResponse"),
                "executableCode": _ref("ExecutableCode"),
                "codeExecutionResult": _ref("CodeExecutionResult"),
                "toolCall": _ref("ToolCall"),
                "toolResponse": _ref("ToolResponse"),
                "videoMetadata": _ref("VideoMetadata"),
                "thought": {"type": "boolean"},
                "thoughtSignature": {
                    "type": "string",
                    "format": "byte",
                },
                "partMetadata": {
                    "type": "object",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        },
        "Blob": {
            "type": "object",
            "description": "Inline bytes for image, audio, or video content.",
            "properties": {
                "mimeType": {"type": "string"},
                "data": {"type": "string", "format": "byte"},
                "displayName": {"type": "string"},
            },
            "required": ["mimeType", "data"],
            "additionalProperties": False,
        },
        "FileData": {
            "type": "object",
            "description": "URI-based file reference used inside message parts.",
            "properties": {
                "mimeType": {"type": "string"},
                "fileUri": {"type": "string"},
                "displayName": {"type": "string"},
            },
            "required": ["fileUri"],
            "additionalProperties": False,
        },
        "FunctionCall": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "args": {"type": "object", "additionalProperties": True},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        "FunctionResponsePart": {
            "type": "object",
            "properties": {
                "inlineData": _ref("Blob"),
                "fileData": _ref("FileData"),
            },
            "additionalProperties": False,
        },
        "FunctionResponse": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "response": {"type": "object", "additionalProperties": True},
                "parts": {
                    "type": "array",
                    "items": _ref("FunctionResponsePart"),
                },
            },
            "required": ["name", "response"],
            "additionalProperties": False,
        },
        "ExecutableCode": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "language": {"type": "string"},
                "code": {"type": "string"},
            },
            "required": ["language", "code"],
            "additionalProperties": False,
        },
        "CodeExecutionResult": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "outcome": {"type": "string"},
                "output": {"type": "string"},
            },
            "required": ["outcome"],
            "additionalProperties": False,
        },
        "ToolCall": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "toolType": {"type": "string"},
                "args": {"type": "object", "additionalProperties": True},
            },
            "additionalProperties": False,
        },
        "ToolResponse": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "toolType": {"type": "string"},
                "response": {"type": "object", "additionalProperties": True},
            },
            "additionalProperties": False,
        },
        "VideoMetadata": {
            "type": "object",
            "properties": {
                "startOffset": _ref("GoogleDuration"),
                "endOffset": _ref("GoogleDuration"),
                "fps": {"type": "number"},
            },
            "additionalProperties": False,
        },
        "Tool": {
            "type": "object",
            "description": "Model tool declaration.",
            "properties": {
                "functionDeclarations": {
                    "type": "array",
                    "items": _ref("FunctionDeclaration"),
                },
                "googleSearchRetrieval": _generic_object("Google Search retrieval tool."),
                "codeExecution": {
                    "type": "object",
                    "description": "Code execution tool.",
                    "additionalProperties": False,
                },
                "googleSearch": _ref("GoogleSearch"),
                "computerUse": _generic_object("Computer Use tool."),
                "urlContext": _ref("UrlContext"),
                "fileSearch": _ref("FileSearch"),
                "mcpServers": {
                    "type": "array",
                    "items": _ref("McpServer"),
                },
                "googleMaps": _ref("GoogleMaps"),
                "googleSearchRetrieval": _ref("GoogleSearchRetrieval"),
                "retrieval": _ref("Retrieval"),
            },
            "additionalProperties": False,
        },
        "ToolConfig": {
            "type": "object",
            "properties": {
                "functionCallingConfig": _ref("FunctionCallingConfig"),
                "retrievalConfig": _ref("RetrievalConfig"),
                "includeServerSideToolInvocations": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
        "ApiSchema": {
            "type": "object",
            "description": "Subset of the Gemini Schema object used for function and response schemas.",
            "properties": {
                "type": {"type": "string"},
                "format": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": "string"},
                "nullable": {"type": "boolean"},
                "enum": {"type": "array", "items": {"type": "string"}},
                "items": {"$ref": "#/components/schemas/ApiSchema"},
                "properties": {
                    "type": "object",
                    "additionalProperties": {"$ref": "#/components/schemas/ApiSchema"},
                },
                "required": {"type": "array", "items": {"type": "string"}},
                "additionalProperties": {
                    "oneOf": [
                        {"type": "boolean"},
                        {"$ref": "#/components/schemas/ApiSchema"},
                    ]
                },
                "anyOf": {
                    "type": "array",
                    "items": {"$ref": "#/components/schemas/ApiSchema"},
                },
                "ref": {"type": "string"},
                "defs": {
                    "type": "object",
                    "additionalProperties": {"$ref": "#/components/schemas/ApiSchema"},
                },
            },
            "additionalProperties": True,
        },
        "FunctionDeclaration": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "parameters": _ref("ApiSchema"),
                "parametersJsonSchema": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "response": _ref("ApiSchema"),
                "responseJsonSchema": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "behavior": {"type": "string"},
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        "LatLng": {
            "type": "object",
            "properties": {
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
            },
            "additionalProperties": False,
        },
        "RetrievalConfig": {
            "type": "object",
            "properties": {
                "latLng": _ref("LatLng"),
                "languageCode": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "FunctionCallingConfig": {
            "type": "object",
            "properties": {
                "allowedFunctionNames": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "mode": {"type": "string"},
                "streamFunctionCallArguments": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
        "GoogleSearch": {
            "type": "object",
            "properties": {
                "searchTypes": _ref("SearchTypes"),
                "blockingConfidence": {"type": "string"},
                "excludeDomains": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "timeRangeFilter": _ref("Interval"),
            },
            "additionalProperties": False,
        },
        "SearchTypes": {
            "type": "object",
            "properties": {
                "webSearch": {
                    "type": "object",
                    "additionalProperties": False,
                },
                "imageSearch": {
                    "type": "object",
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
        "Interval": {
            "type": "object",
            "properties": {
                "startTime": _ref("GoogleTimestamp"),
                "endTime": _ref("GoogleTimestamp"),
            },
            "additionalProperties": False,
        },
        "GoogleMaps": {
            "type": "object",
            "properties": {
                "authConfig": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "enableWidget": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
        "DynamicRetrievalConfig": {
            "type": "object",
            "properties": {
                "dynamicThreshold": {"type": "number"},
                "mode": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GoogleSearchRetrieval": {
            "type": "object",
            "properties": {
                "dynamicRetrievalConfig": _ref("DynamicRetrievalConfig"),
            },
            "additionalProperties": False,
        },
        "FileSearch": {
            "type": "object",
            "properties": {
                "fileSearchStoreNames": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "topK": {"type": "integer"},
                "metadataFilter": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "Retrieval": {
            "type": "object",
            "properties": {
                "disableAttribution": {"type": "boolean"},
                "externalApi": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "vertexAiSearch": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "vertexRagStore": {
                    "type": "object",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        },
        "UrlContext": {
            "type": "object",
            "additionalProperties": False,
        },
        "McpServer": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "streamableHttpTransport": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string"},
                        "headers": {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        },
                        "timeout": {"type": "string"},
                        "sseReadTimeout": {"type": "string"},
                        "terminateOnClose": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
        "SafetySetting": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "method": {"type": "string"},
                "threshold": {"type": "string"},
            },
            "required": ["category", "threshold"],
            "additionalProperties": False,
        },
        "SafetyRating": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "probability": {"type": "string"},
                "blocked": {"type": "boolean"},
                "overwrittenThreshold": {"type": "string"},
                "probabilityScore": {"type": "number"},
                "severity": {"type": "string"},
                "severityScore": {"type": "number"},
            },
            "required": ["category", "probability"],
            "additionalProperties": False,
        },
        "GenerationConfig": {
            "type": "object",
            "description": "Configuration options for model generation and outputs.",
            "properties": {
                "temperature": {"type": "number"},
                "topP": {"type": "number"},
                "topK": {"type": "number"},
                "candidateCount": {"type": "integer"},
                "maxOutputTokens": {"type": "integer"},
                "stopSequences": {"type": "array", "items": {"type": "string"}},
                "responseMimeType": {"type": "string"},
                "responseSchema": _ref("ApiSchema"),
                "responseJsonSchema": {"type": "object", "additionalProperties": True},
                "responseModalities": {"type": "array", "items": {"type": "string"}},
                "presencePenalty": {"type": "number"},
                "frequencyPenalty": {"type": "number"},
                "seed": {"type": "integer"},
                "responseLogprobs": {"type": "boolean"},
                "logprobs": {"type": "integer"},
                "toolConfig": _ref("ToolConfig"),
                "automaticFunctionCalling": _ref("AutomaticFunctionCallingConfig"),
                "thinkingConfig": _ref("ThinkingConfig"),
                "imageConfig": _ref("ImageConfig"),
                "speechConfig": _ref("SpeechConfig"),
            },
            "additionalProperties": False,
        },
        "AutomaticFunctionCallingConfig": {
            "type": "object",
            "properties": {
                "disable": {"type": "boolean"},
                "maximumRemoteCalls": {"type": "integer"},
                "ignoreCallHistory": {"type": "boolean"},
            },
            "additionalProperties": False,
        },
        "ThinkingConfig": {
            "type": "object",
            "properties": {
                "includeThoughts": {"type": "boolean"},
                "thinkingBudget": {"type": "integer"},
                "thinkingLevel": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "SpeechConfig": {
            "type": "object",
            "properties": {
                "languageCode": {"type": "string"},
                "voiceConfig": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "multiSpeakerVoiceConfig": {
                    "type": "object",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        },
        "ImageConfig": {
            "type": "object",
            "properties": {
                "aspectRatio": {"type": "string"},
                "imageSize": {"type": "string"},
                "personGeneration": {"type": "string"},
                "prominentPeople": {"type": "string"},
                "outputMimeType": {"type": "string"},
                "outputCompressionQuality": {"type": "integer"},
                "imageOutputOptions": {
                    "type": "object",
                    "properties": {
                        "mimeType": {"type": "string"},
                        "compressionQuality": {"type": "integer"},
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
        "GenerateContentRequest": {
            "type": "object",
            "properties": {
                "contents": {
                    "type": "array",
                    "items": _ref("Content"),
                },
                "tools": {
                    "type": "array",
                    "items": _ref("Tool"),
                },
                "toolConfig": _ref("ToolConfig"),
                "safetySettings": {
                    "type": "array",
                    "items": _ref("SafetySetting"),
                },
                "systemInstruction": _ref("Content"),
                "generationConfig": _ref("GenerationConfig"),
                "cachedContent": {"type": "string"},
                "store": {"type": "boolean"},
            },
            "required": ["contents"],
            "additionalProperties": False,
        },
        "GenerateContentCandidate": {
            "type": "object",
            "properties": {
                "content": _ref("Content"),
                "finishReason": {"type": "string"},
                "finishMessage": {"type": "string"},
                "safetyRatings": {
                    "type": "array",
                    "items": _ref("SafetyRating"),
                },
                "citationMetadata": _ref("CitationMetadata"),
                "tokenCount": {"type": "integer"},
                "groundingAttributions": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "groundingMetadata": _ref("GroundingMetadata"),
                "avgLogprobs": {"type": "number"},
                "logprobsResult": _ref("LogprobsResult"),
                "urlContextMetadata": _ref("UrlContextMetadata"),
                "index": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "GenerateContentPromptFeedback": {
            "type": "object",
            "properties": {
                "blockReason": {"type": "string"},
                "safetyRatings": {
                    "type": "array",
                    "items": _ref("SafetyRating"),
                },
            },
            "additionalProperties": False,
        },
        "Citation": {
            "type": "object",
            "properties": {
                "startIndex": {"type": "integer"},
                "endIndex": {"type": "integer"},
                "uri": {"type": "string"},
                "title": {"type": "string"},
                "license": {"type": "string"},
                "publicationDate": {
                    "type": "object",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        },
        "CitationMetadata": {
            "type": "object",
            "properties": {
                "citations": {
                    "type": "array",
                    "items": _ref("Citation"),
                }
            },
            "additionalProperties": False,
        },
        "Segment": {
            "type": "object",
            "properties": {
                "startIndex": {"type": "integer"},
                "endIndex": {"type": "integer"},
                "partIndex": {"type": "integer"},
                "text": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingChunk": {
            "type": "object",
            "properties": {
                "web": _ref("GroundingChunkWeb"),
                "retrievedContext": _ref("GroundingChunkRetrievedContext"),
                "maps": _ref("GroundingChunkMaps"),
                "image": _ref("GroundingChunkImage"),
            },
            "additionalProperties": False,
        },
        "GroundingChunkMapsAuthorAttribution": {
            "type": "object",
            "properties": {
                "displayName": {"type": "string"},
                "photoUri": {"type": "string"},
                "uri": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingChunkMapsReviewSnippet": {
            "type": "object",
            "properties": {
                "authorAttribution": _ref("GroundingChunkMapsAuthorAttribution"),
                "flagContentUri": {"type": "string"},
                "googleMapsUri": {"type": "string"},
                "relativePublishTimeDescription": {"type": "string"},
                "review": {"type": "string"},
                "reviewId": {"type": "string"},
                "title": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingChunkMapsPlaceAnswerSources": {
            "type": "object",
            "properties": {
                "reviewSnippet": {
                    "type": "array",
                    "items": _ref("GroundingChunkMapsReviewSnippet"),
                },
                "reviewSnippets": {
                    "type": "array",
                    "items": _ref("GroundingChunkMapsReviewSnippet"),
                },
                "flagContentUri": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingChunkMapsRoute": {
            "type": "object",
            "properties": {
                "distanceMeters": {"type": "integer"},
                "duration": _ref("GoogleDuration"),
                "encodedPolyline": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingChunkMaps": {
            "type": "object",
            "properties": {
                "placeAnswerSources": _ref("GroundingChunkMapsPlaceAnswerSources"),
                "placeId": {"type": "string"},
                "text": {"type": "string"},
                "title": {"type": "string"},
                "uri": {"type": "string"},
                "route": _ref("GroundingChunkMapsRoute"),
            },
            "additionalProperties": False,
        },
        "GroundingChunkImage": {
            "type": "object",
            "properties": {
                "sourceUri": {"type": "string"},
                "imageUri": {"type": "string"},
                "title": {"type": "string"},
                "domain": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "RagChunkPageSpan": {
            "type": "object",
            "properties": {
                "firstPage": {"type": "integer"},
                "lastPage": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "RagChunk": {
            "type": "object",
            "properties": {
                "pageSpan": _ref("RagChunkPageSpan"),
                "text": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingChunkStringList": {
            "type": "object",
            "properties": {
                "values": {
                    "type": "array",
                    "items": {"type": "string"},
                }
            },
            "additionalProperties": False,
        },
        "GroundingChunkCustomMetadata": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "numericValue": {"type": "number"},
                "stringValue": {"type": "string"},
                "stringListValue": _ref("GroundingChunkStringList"),
            },
            "additionalProperties": False,
        },
        "GroundingChunkRetrievedContext": {
            "type": "object",
            "properties": {
                "documentName": {"type": "string"},
                "ragChunk": _ref("RagChunk"),
                "text": {"type": "string"},
                "title": {"type": "string"},
                "uri": {"type": "string"},
                "customMetadata": {
                    "type": "array",
                    "items": _ref("GroundingChunkCustomMetadata"),
                },
                "fileSearchStore": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingChunkWeb": {
            "type": "object",
            "properties": {
                "domain": {"type": "string"},
                "title": {"type": "string"},
                "uri": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingSupport": {
            "type": "object",
            "properties": {
                "groundingChunkIndices": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
                "confidenceScores": {
                    "type": "array",
                    "items": {"type": "number"},
                },
                "segment": _ref("Segment"),
                "renderedParts": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
            },
            "additionalProperties": False,
        },
        "RetrievalMetadata": {
            "type": "object",
            "properties": {
                "googleSearchDynamicRetrievalScore": {"type": "number"},
            },
            "additionalProperties": False,
        },
        "SearchEntryPoint": {
            "type": "object",
            "properties": {
                "renderedContent": {"type": "string"},
                "sdkBlob": {"type": "string", "format": "byte"},
            },
            "additionalProperties": False,
        },
        "GroundingMetadataSourceFlaggingUri": {
            "type": "object",
            "properties": {
                "flagContentUri": {"type": "string"},
                "sourceId": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "GroundingMetadata": {
            "type": "object",
            "properties": {
                "imageSearchQueries": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "groundingChunks": {
                    "type": "array",
                    "items": _ref("GroundingChunk"),
                },
                "groundingSupports": {
                    "type": "array",
                    "items": _ref("GroundingSupport"),
                },
                "retrievalMetadata": _ref("RetrievalMetadata"),
                "searchEntryPoint": _ref("SearchEntryPoint"),
                "webSearchQueries": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "googleMapsWidgetContextToken": {"type": "string"},
                "retrievalQueries": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "sourceFlaggingUris": {
                    "type": "array",
                    "items": _ref("GroundingMetadataSourceFlaggingUri"),
                },
            },
            "additionalProperties": False,
        },
        "LogprobsResultCandidate": {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "tokenId": {"type": "integer"},
                "logProbability": {"type": "number"},
            },
            "additionalProperties": False,
        },
        "LogprobsResultTopCandidates": {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": _ref("LogprobsResultCandidate"),
                }
            },
            "additionalProperties": False,
        },
        "LogprobsResult": {
            "type": "object",
            "properties": {
                "chosenCandidates": {
                    "type": "array",
                    "items": _ref("LogprobsResultCandidate"),
                },
                "topCandidates": {
                    "type": "array",
                    "items": _ref("LogprobsResultTopCandidates"),
                },
                "logProbabilitySum": {"type": "number"},
            },
            "additionalProperties": False,
        },
        "UrlMetadata": {
            "type": "object",
            "properties": {
                "retrievedUrl": {"type": "string"},
                "urlRetrievalStatus": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "UrlContextMetadata": {
            "type": "object",
            "properties": {
                "urlMetadata": {
                    "type": "array",
                    "items": _ref("UrlMetadata"),
                }
            },
            "additionalProperties": False,
        },
        "ModalityTokenCount": {
            "type": "object",
            "properties": {
                "modality": {"type": "string"},
                "tokenCount": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "GenerateContentUsageMetadata": {
            "type": "object",
            "properties": {
                "promptTokenCount": {"type": "integer"},
                "cachedContentTokenCount": {"type": "integer"},
                "candidatesTokenCount": {"type": "integer"},
                "toolUsePromptTokenCount": {"type": "integer"},
                "thoughtsTokenCount": {"type": "integer"},
                "totalTokenCount": {"type": "integer"},
                "promptTokensDetails": {
                    "type": "array",
                    "items": _ref("ModalityTokenCount"),
                },
                "cacheTokensDetails": {
                    "type": "array",
                    "items": _ref("ModalityTokenCount"),
                },
                "candidatesTokensDetails": {
                    "type": "array",
                    "items": _ref("ModalityTokenCount"),
                },
                "toolUsePromptTokensDetails": {
                    "type": "array",
                    "items": _ref("ModalityTokenCount"),
                },
            },
            "additionalProperties": False,
        },
        "ModelStatus": {
            "type": "object",
            "properties": {
                "modelStage": {"type": "string"},
                "retirementTime": _ref("GoogleTimestamp"),
            },
            "additionalProperties": False,
        },
        "GenerateContentResponse": {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": _ref("GenerateContentCandidate"),
                },
                "promptFeedback": _ref("GenerateContentPromptFeedback"),
                "usageMetadata": _ref("GenerateContentUsageMetadata"),
                "modelVersion": {"type": "string"},
                "responseId": {"type": "string"},
                "modelStatus": _ref("ModelStatus"),
            },
            "additionalProperties": False,
        },
        "EmbedContentRequest": {
            "type": "object",
            "properties": {
                "content": _ref("Content"),
                "taskType": {"type": "string"},
                "title": {"type": "string"},
                "outputDimensionality": {"type": "integer"},
            },
            "required": ["content"],
            "additionalProperties": False,
        },
        "ContentEmbedding": {
            "type": "object",
            "properties": {
                "values": {
                    "type": "array",
                    "items": {"type": "number"},
                },
                "shape": {
                    "type": "array",
                    "items": {"type": "integer"},
                },
            },
            "additionalProperties": False,
        },
        "EmbedContentResponse": {
            "type": "object",
            "properties": {
                "embedding": _ref("ContentEmbedding"),
            },
            "additionalProperties": False,
        },
        "BatchEmbedContentsRequest": {
            "type": "object",
            "properties": {
                "requests": {
                    "type": "array",
                    "items": _ref("EmbedContentRequest"),
                },
            },
            "required": ["requests"],
            "additionalProperties": False,
        },
        "BatchEmbedContentsResponse": {
            "type": "object",
            "properties": {
                "embeddings": {
                    "type": "array",
                    "items": _ref("ContentEmbedding"),
                }
            },
            "additionalProperties": False,
        },
        "FileStatus": {
            "type": "object",
            "properties": {
                "details": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "message": {"type": "string"},
                "code": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "File": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "displayName": {"type": "string"},
                "mimeType": {"type": "string"},
                "sizeBytes": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
                "createTime": _ref("GoogleTimestamp"),
                "updateTime": _ref("GoogleTimestamp"),
                "expirationTime": _ref("GoogleTimestamp"),
                "sha256Hash": {"type": "string"},
                "uri": {"type": "string"},
                "downloadUri": {
                    "type": "string",
                    "description": (
                        "Download URI for downloadable files, such as generated batch result "
                        "files. The official Files guide says uploaded files cannot be "
                        "downloaded."
                    ),
                },
                "state": {
                    "type": "string",
                    "enum": ["STATE_UNSPECIFIED", "PROCESSING", "ACTIVE", "FAILED"],
                },
                "source": {
                    "type": "string",
                    "enum": ["SOURCE_UNSPECIFIED", "UPLOADED", "GENERATED", "REGISTERED"],
                    "description": (
                        "Use `GENERATED` plus `downloadUri` or the guide-documented "
                        "`/download/v1beta/...:download` route for downloadable batch result "
                        "files. Uploaded files are not downloadable."
                    ),
                },
                "videoMetadata": {"type": "object", "additionalProperties": True},
                "error": _ref("FileStatus"),
            },
            "additionalProperties": False,
        },
        "CreateFileRequest": {
            "type": "object",
            "properties": {
                "file": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "displayName": {"type": "string"},
                        "mimeType": {"type": "string"},
                    },
                    "additionalProperties": False,
                }
            },
            "additionalProperties": False,
        },
        "MediaUploadResponse": {
            "type": "object",
            "properties": {
                "file": _ref("File"),
            },
            "additionalProperties": False,
        },
        "StringList": {
            "type": "object",
            "properties": {
                "values": {
                    "type": "array",
                    "items": {"type": "string"},
                }
            },
            "additionalProperties": False,
        },
        "CustomMetadata": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "numericValue": {"type": "number"},
                "stringListValue": _ref("StringList"),
                "stringValue": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "WhiteSpaceConfig": {
            "type": "object",
            "properties": {
                "maxTokensPerChunk": {"type": "integer"},
                "maxOverlapTokens": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "ChunkingConfig": {
            "type": "object",
            "properties": {
                "whiteSpaceConfig": _ref("WhiteSpaceConfig"),
            },
            "additionalProperties": False,
        },
        "JobError": {
            "type": "object",
            "properties": {
                "details": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "message": {"type": "string"},
                "code": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "BatchJobState": {
            "type": "string",
            "enum": [
                "JOB_STATE_UNSPECIFIED",
                "JOB_STATE_QUEUED",
                "JOB_STATE_PENDING",
                "JOB_STATE_RUNNING",
                "JOB_STATE_SUCCEEDED",
                "JOB_STATE_FAILED",
                "JOB_STATE_CANCELLING",
                "JOB_STATE_CANCELLED",
                "JOB_STATE_PAUSED",
                "JOB_STATE_EXPIRED",
                "JOB_STATE_UPDATING",
                "JOB_STATE_PARTIALLY_SUCCEEDED",
            ],
        },
        "BatchState": {
            "type": "string",
            "enum": [
                "BATCH_STATE_UNSPECIFIED",
                "BATCH_STATE_PENDING",
                "BATCH_STATE_RUNNING",
                "BATCH_STATE_SUCCEEDED",
                "BATCH_STATE_FAILED",
                "BATCH_STATE_CANCELLED",
                "BATCH_STATE_EXPIRED",
            ],
        },
        "BatchStats": {
            "type": "object",
            "properties": {
                "requestCount": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
                "successfulRequestCount": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
                "failedRequestCount": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
                "pendingRequestCount": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
            },
            "additionalProperties": False,
        },
        "BatchGenerateRequest": {
            "type": "object",
            "properties": {
                "request": {
                    "type": "object",
                    "properties": {
                        "model": {"type": "string"},
                        "contents": {
                            "type": "array",
                            "items": _ref("Content"),
                        },
                        "generationConfig": _ref("GenerationConfig"),
                    },
                    "additionalProperties": False,
                },
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
            "additionalProperties": False,
        },
        "BatchGenerateRequestsEnvelope": {
            "type": "object",
            "properties": {
                "requests": {
                    "type": "array",
                    "items": _ref("BatchGenerateRequest"),
                }
            },
            "additionalProperties": False,
        },
        "BatchGenerateContentInputConfig": {
            "type": "object",
            "properties": {
                "fileName": {"type": "string"},
                "requests": _ref("BatchGenerateRequestsEnvelope"),
            },
            "additionalProperties": False,
        },
        "GenerateContentBatchOutput": {
            "type": "object",
            "properties": {
                "responsesFile": {"type": "string"},
                "inlinedResponses": _ref("InlinedResponsesContainer"),
            },
            "additionalProperties": False,
        },
        "BatchGenerateContentResource": {
            "type": "object",
            "properties": {
                "displayName": {"type": "string"},
                "inputConfig": _ref("BatchGenerateContentInputConfig"),
            },
            "required": ["inputConfig"],
            "additionalProperties": False,
        },
        "CreateBatchGenerateContentRequest": {
            "type": "object",
            "properties": {
                "batch": _ref("BatchGenerateContentResource"),
            },
            "required": ["batch"],
            "additionalProperties": False,
        },
        "BatchEmbedRequest": {
            "type": "object",
            "properties": {
                "request": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "array",
                            "items": _ref("Content"),
                        }
                    },
                    "required": ["content"],
                    "additionalProperties": False,
                },
                "taskType": {"type": "string"},
                "title": {"type": "string"},
                "outputDimensionality": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "BatchEmbedRequestsEnvelope": {
            "type": "object",
            "properties": {
                "requests": {
                    "type": "array",
                    "items": _ref("BatchEmbedRequest"),
                }
            },
            "additionalProperties": False,
        },
        "BatchEmbedContentInputConfig": {
            "type": "object",
            "properties": {
                "fileName": {"type": "string"},
                "requests": _ref("BatchEmbedRequestsEnvelope"),
            },
            "additionalProperties": False,
        },
        "EmbedContentBatchOutput": {
            "type": "object",
            "properties": {
                "responsesFile": {"type": "string"},
                "inlinedEmbedContentResponses": _ref(
                    "InlinedEmbedContentResponsesContainer"
                ),
            },
            "additionalProperties": False,
        },
        "BatchEmbedContentResource": {
            "type": "object",
            "properties": {
                "displayName": {"type": "string"},
                "inputConfig": _ref("BatchEmbedContentInputConfig"),
            },
            "required": ["inputConfig"],
            "additionalProperties": False,
        },
        "CreateBatchEmbedContentRequest": {
            "type": "object",
            "properties": {
                "batch": _ref("BatchEmbedContentResource"),
            },
            "required": ["batch"],
            "additionalProperties": False,
        },
        "InlinedResponse": {
            "type": "object",
            "properties": {
                "response": _ref("GenerateContentResponse"),
                "metadata": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "error": _ref("JobError"),
            },
            "additionalProperties": False,
        },
        "InlinedResponsesContainer": {
            "type": "object",
            "properties": {
                "inlinedResponses": {
                    "type": "array",
                    "items": _ref("InlinedResponse"),
                }
            },
            "additionalProperties": False,
        },
        "SingleEmbedContentResponse": {
            "type": "object",
            "properties": {
                "embedding": _ref("ContentEmbedding"),
                "tokenCount": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "InlinedEmbedContentResponse": {
            "type": "object",
            "properties": {
                "response": _ref("SingleEmbedContentResponse"),
                "error": _ref("JobError"),
                "metadata": {
                    "type": "object",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": False,
        },
        "InlinedEmbedContentResponsesContainer": {
            "type": "object",
            "properties": {
                "inlinedResponses": {
                    "type": "array",
                    "items": _ref("InlinedEmbedContentResponse"),
                }
            },
            "additionalProperties": False,
        },
        "BatchOperationOutput": {
            "type": "object",
            "properties": {
                "responsesFile": {"type": "string"},
                "inlinedResponses": _ref("InlinedResponsesContainer"),
                "inlinedEmbedContentResponses": _ref(
                    "InlinedEmbedContentResponsesContainer"
                ),
            },
            "additionalProperties": False,
        },
        "BatchOperationMetadata": {
            "type": "object",
            "properties": {
                "displayName": {"type": "string"},
                "state": _ref("BatchJobState"),
                "createTime": _ref("GoogleTimestamp"),
                "endTime": _ref("GoogleTimestamp"),
                "updateTime": _ref("GoogleTimestamp"),
                "model": {"type": "string"},
                "output": _ref("BatchOperationOutput"),
                "batchStats": _ref("BatchStats"),
                "priority": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
            },
            "additionalProperties": False,
        },
        "BatchOperation": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "done": {"type": "boolean"},
                "metadata": _ref("BatchOperationMetadata"),
                "response": _ref("BatchOperationOutput"),
                "error": _ref("JobError"),
            },
            "additionalProperties": False,
        },
        "ListBatchesResponse": {
            "type": "object",
            "properties": {
                "operations": {
                    "type": "array",
                    "items": _ref("BatchOperation"),
                },
                "nextPageToken": {"type": "string"},
                "unreachable": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "additionalProperties": False,
        },
        "GenerateContentBatch": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "model": {"type": "string"},
                "displayName": {"type": "string"},
                "inputConfig": _ref("BatchGenerateContentInputConfig"),
                "output": _ref("GenerateContentBatchOutput"),
                "createTime": _ref("GoogleTimestamp"),
                "endTime": _ref("GoogleTimestamp"),
                "updateTime": _ref("GoogleTimestamp"),
                "batchStats": _ref("BatchStats"),
                "state": _ref("BatchState"),
                "priority": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
            },
            "additionalProperties": False,
        },
        "EmbedContentBatch": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "model": {"type": "string"},
                "displayName": {"type": "string"},
                "inputConfig": _ref("BatchEmbedContentInputConfig"),
                "output": _ref("EmbedContentBatchOutput"),
                "createTime": _ref("GoogleTimestamp"),
                "endTime": _ref("GoogleTimestamp"),
                "updateTime": _ref("GoogleTimestamp"),
                "batchStats": _ref("BatchStats"),
                "state": _ref("BatchState"),
                "priority": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
            },
            "additionalProperties": False,
        },
        "LongRunningOperation": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "metadata": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Operation-specific metadata. Structure varies by endpoint.",
                },
                "done": {"type": "boolean"},
                "error": _ref("JobError"),
                "response": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Operation result. Structure varies by endpoint.",
                },
            },
            "additionalProperties": False,
        },
        "Model": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "baseModelId": {"type": "string"},
                "version": {"type": "string"},
                "displayName": {"type": "string"},
                "description": {"type": "string"},
                "inputTokenLimit": {"type": "integer"},
                "outputTokenLimit": {"type": "integer"},
                "supportedGenerationMethods": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "thinking": {"type": "boolean"},
                "temperature": {"type": "number"},
                "maxTemperature": {"type": "number"},
                "topP": {"type": "number"},
                "topK": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "ListModelsResponse": {
            "type": "object",
            "properties": {
                "models": {
                    "type": "array",
                    "items": _ref("Model"),
                },
                "nextPageToken": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "FileSearchStore": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "displayName": {"type": "string"},
                "createTime": _ref("GoogleTimestamp"),
                "updateTime": _ref("GoogleTimestamp"),
                "activeDocumentsCount": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
                "pendingDocumentsCount": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
                "failedDocumentsCount": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
                "sizeBytes": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
            },
            "additionalProperties": False,
        },
        "CreateFileSearchStoreRequest": {
            "type": "object",
            "properties": {
                "displayName": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "ListFileSearchStoresResponse": {
            "type": "object",
            "properties": {
                "fileSearchStores": {
                    "type": "array",
                    "items": _ref("FileSearchStore"),
                },
                "nextPageToken": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "ImportFileRequest": {
            "type": "object",
            "properties": {
                "fileName": {"type": "string"},
                "customMetadata": {
                    "type": "array",
                    "items": _ref("CustomMetadata"),
                },
                "chunkingConfig": _ref("ChunkingConfig"),
            },
            "required": ["fileName"],
            "additionalProperties": False,
        },
        "UploadToFileSearchStoreMetadataRequest": {
            "type": "object",
            "properties": {
                "displayName": {"type": "string"},
                "customMetadata": {
                    "type": "array",
                    "items": _ref("CustomMetadata"),
                },
                "chunkingConfig": _ref("ChunkingConfig"),
                "mimeType": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "DocumentState": {
            "type": "string",
            "enum": [
                "STATE_UNSPECIFIED",
                "STATE_PENDING",
                "STATE_ACTIVE",
                "STATE_FAILED",
            ],
        },
        "Document": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "displayName": {"type": "string"},
                "customMetadata": {
                    "type": "array",
                    "items": _ref("CustomMetadata"),
                },
                "updateTime": _ref("GoogleTimestamp"),
                "createTime": _ref("GoogleTimestamp"),
                "state": _ref("DocumentState"),
                "sizeBytes": {
                    "type": "string",
                    "description": "Int64 encoded as a string.",
                },
                "mimeType": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "ListDocumentsResponse": {
            "type": "object",
            "properties": {
                "documents": {
                    "type": "array",
                    "items": _ref("Document"),
                },
                "nextPageToken": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "AuthToken": {
            "type": "object",
            "description": (
                "Ephemeral token that constrains BidiGenerateContent (Live API) "
                "sessions created with it."
            ),
            "properties": {
                "name": {
                    "type": "string",
                    "description": (
                        "Auth token name in the form `auth_tokens/{token}`. Pass it "
                        "as the API key when connecting to BidiGenerateContent "
                        "sessions."
                    ),
                },
                "expireTime": _ref("GoogleTimestamp"),
                "newSessionExpireTime": _ref("GoogleTimestamp"),
                "uses": {
                    "type": "integer",
                    "description": (
                        "Remaining number of times the token can be used. Resuming "
                        "a session does not count as a use."
                    ),
                },
            },
            "required": ["name"],
            "additionalProperties": False,
        },
        "CreateAuthTokenRequest": {
            "type": "object",
            "description": (
                "Request for `auth_tokens.create`. Field names follow the "
                "python-genai SDK wire format."
            ),
            "properties": {
                "expireTime": _ref("GoogleTimestamp"),
                "newSessionExpireTime": _ref("GoogleTimestamp"),
                "uses": {
                    "type": "integer",
                    "description": (
                        "Number of times the token can be used. Zero means no "
                        "limit. Resuming a session does not count as a use. "
                        "Defaults to 1."
                    ),
                },
                "bidiGenerateContentSetup": _ref("BidiGenerateContentSetup"),
                "fieldMask": {
                    "type": "string",
                    "description": (
                        "Comma-separated list of Live API setup fields locked by "
                        "the token. Absent means the whole setup is locked."
                    ),
                },
            },
            "additionalProperties": False,
        },
        "BidiGenerateContentSetup": {
            "type": "object",
            "description": (
                "Locked BidiGenerateContent (Live API) session parameters applied "
                "to every session created with the token. Mirrors the Live API "
                "`setup` message."
            ),
            "properties": {
                "model": {
                    "type": "string",
                    "description": "ID of the model to configure for Live API sessions.",
                },
            },
            "additionalProperties": True,
        },
        "EnvironmentFile": {
            "type": "object",
            "description": (
                "Metadata for a file or directory within a Code Execution "
                "environment snapshot. Unlike the proto-JSON surfaces, this "
                "endpoint serializes fields in snake_case (matching the "
                "python-genai GAOS wire format)."
            ),
            "properties": {
                "name": {"type": "string"},
                "path": {
                    "type": "string",
                    "description": "Full relative path within the environment, e.g. `workspace/src/main.py`.",
                },
                "type": {
                    "type": "string",
                    "enum": ["file", "directory"],
                },
                "mime_type": {
                    "type": "string",
                    "description": "MIME type of the file. Empty for directories.",
                },
                "size_bytes": {
                    "type": "integer",
                    "format": "int64",
                    "description": "Size of the file or directory in bytes.",
                },
                "created": _ref("GoogleTimestamp"),
                "modified": _ref("GoogleTimestamp"),
            },
            "additionalProperties": False,
        },
        "GetEnvironmentFilesResponse": {
            "type": "object",
            "description": (
                "Response for retrieving files from an environment snapshot. When "
                "the requested path is a directory this contains its contents; "
                "when it is a file this contains a single metadata entry. Fields "
                "are snake_case, matching the python-genai GAOS wire format."
            ),
            "properties": {
                "files": {
                    "type": "array",
                    "items": _ref("EnvironmentFile"),
                },
                "next_page_token": {"type": "string"},
            },
            "additionalProperties": False,
        },
        # ------------------------------------------------------------------
        # Agent Platform (GAOS) resources: agents, interactions, credentials,
        # environments, triggers, and webhooks. Added to the all-methods index
        # in September 2026. The Discovery export does not cover them, so the
        # shapes below are modeled from the python-genai SDK GAOS surface
        # (`google/genai/_gaos`), which serializes snake_case JSON.
        # ------------------------------------------------------------------
        "Agent": {
            "type": "object",
            "description": (
                "An agent definition (Agent Platform). Fields are snake_case, "
                "matching the python-genai GAOS wire format."
            ),
            "properties": {
                "id": {
                    "type": "string",
                    "description": "The unique identifier for the agent.",
                },
                "base_agent": {
                    "type": "string",
                    "description": "The base agent to extend.",
                },
                "system_instruction": {
                    "type": "string",
                    "description": "System instruction for the agent.",
                },
                "description": {
                    "type": "string",
                    "description": (
                        "Agent description for developers to quickly read and "
                        "understand."
                    ),
                },
                "agent_config": _ref("AntigravityAgentConfig"),
                "base_environment": {
                    "oneOf": [
                        _ref("InteractionEnvironment"),
                        {"type": "string"},
                    ],
                    "description": (
                        "The environment configuration for the agent: either an "
                        "inline remote-environment object or an environment ID."
                    ),
                },
                "tools": {
                    "type": "array",
                    "items": _ref("AgentTool"),
                    "description": "The tools available to the agent.",
                },
            },
            "additionalProperties": False,
        },
        "AntigravityAgentConfig": {
            "type": "object",
            "description": "Configuration parameters for an Antigravity agent.",
            "properties": {
                "type": {"const": "antigravity"},
                "model": {
                    "type": "string",
                    "description": "Model the agent runs with.",
                },
                "max_total_tokens": {
                    "type": "integer",
                    "format": "int64",
                    "description": "Maximum total tokens for the agent.",
                },
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "AgentTool": {
            "oneOf": [
                _ref("AgentCodeExecutionTool"),
                _ref("AgentUrlContextTool"),
                _ref("AgentGoogleSearchTool"),
                _ref("AgentFunctionTool"),
                _ref("AgentMcpServerTool"),
            ],
            "description": (
                "A tool available to an agent. Discriminated by its `type` field."
            ),
        },
        "AgentCodeExecutionTool": {
            "type": "object",
            "description": "Enables code execution for an agent.",
            "properties": {"type": {"const": "code_execution"}},
            "required": ["type"],
            "additionalProperties": False,
        },
        "AgentUrlContextTool": {
            "type": "object",
            "description": "Enables URL context grounding for an agent.",
            "properties": {"type": {"const": "url_context"}},
            "required": ["type"],
            "additionalProperties": False,
        },
        "AgentGoogleSearchTool": {
            "type": "object",
            "description": "Enables Google Search grounding for an agent.",
            "properties": {
                "type": {"const": "google_search"},
                "search_types": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "web_search",
                            "image_search",
                            "enterprise_web_search",
                        ],
                    },
                },
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "AgentFunctionTool": {
            "type": "object",
            "description": "A function (callable tool) available to an agent.",
            "properties": {
                "type": {"const": "function"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "parameters": {
                    "description": (
                        "JSON Schema for the function parameters, when the agent "
                        "calls it with structured arguments."
                    ),
                },
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "AgentMcpServerTool": {
            "type": "object",
            "description": "An MCP server exposed to an agent as a tool.",
            "properties": {
                "type": {"const": "mcp_server"},
                "url": {
                    "type": "string",
                    "format": "uri",
                    "description": "MCP server endpoint URL.",
                },
                "name": {"type": "string"},
                "headers": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                    "description": "HTTP headers sent to the MCP server.",
                },
                "allowed_tools": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "mode": {
                                "type": "string",
                                "description": "Tool choice mode.",
                            },
                            "tools": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Allowed tool names.",
                            },
                        },
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "ListAgentsResponse": {
            "type": "object",
            "description": "Response for listing agents.",
            "properties": {
                "agents": {"type": "array", "items": _ref("Agent")},
                "next_page_token": {
                    "type": "string",
                    "description": (
                        "A token to retrieve the next page of results."
                    ),
                },
            },
            "additionalProperties": False,
        },
        "Interaction": {
            "type": "object",
            "description": (
                "An Agent Platform interaction: a stateful execution of an agent "
                "or model with inputs, steps, and outputs. Fields are snake_case, "
                "matching the python-genai GAOS wire format."
            ),
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Output only. The ID of the interaction.",
                },
                "status": {
                    "type": "string",
                    "enum": [
                        "in_progress",
                        "requires_action",
                        "completed",
                        "failed",
                        "cancelled",
                        "incomplete",
                        "budget_exceeded",
                        "queued",
                    ],
                    "description": "Output only. The status of the interaction.",
                },
                "agent": {
                    "type": "string",
                    "description": (
                        "Agent option for agent-backed interactions, e.g. "
                        "`antigravity-preview-05-2026` or a Deep Research agent ID."
                    ),
                },
                "model": {
                    "type": "string",
                    "description": "Model for model-backed interactions.",
                },
                "input": _ref("InteractionsInput"),
                "steps": {
                    "type": "array",
                    "items": _ref("InteractionStep"),
                    "description": "Output only. The interaction's execution steps.",
                },
                "output_text": {
                    "type": "string",
                    "description": "Output only. Convenience text output.",
                },
                "output_audio": _ref("InteractionContent"),
                "output_image": _ref("InteractionContent"),
                "output_video": _ref("InteractionContent"),
                "agent_config": {
                    "type": "object",
                    "description": "Agent configuration for this interaction.",
                    "additionalProperties": True,
                },
                "generation_config": _ref("InteractionGenerationConfig"),
                "cached_content": {
                    "type": "string",
                    "description": "Cached content resource for model interactions.",
                },
                "created": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Output only. Creation time (ISO 8601).",
                },
                "updated": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Output only. Last update time (ISO 8601).",
                },
                "environment": _ref("InteractionEnvironment"),
                "environment_id": {"type": "string"},
                "errors": {
                    "type": "array",
                    "items": _ref("InteractionError"),
                    "description": "Output only. Errors produced by the interaction.",
                },
                "labels": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "previous_interaction_id": {
                    "type": "string",
                    "description": "ID of the interaction this one continues.",
                },
                "response_format": {
                    "type": "object",
                    "description": "Structured output format for the interaction.",
                    "additionalProperties": True,
                },
                "response_mime_type": {"type": "string"},
                "response_modalities": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["text", "image", "audio", "video", "document"],
                    },
                },
                "safety_settings": {
                    "type": "array",
                    "items": _ref("InteractionSafetySetting"),
                },
                "service_tier": {
                    "type": "string",
                    "enum": ["flex", "standard", "priority", "deferred"],
                },
                "system_instruction": {"type": "string"},
                "tools": {
                    "type": "array",
                    "description": "Tools available to the interaction.",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "usage": _ref("InteractionUsage"),
                "webhook_config": _ref("InteractionWebhookConfig"),
            },
            "required": ["status"],
            "additionalProperties": False,
        },
        "InteractionsInput": {
            "oneOf": [
                {"type": "string"},
                _ref("InteractionContent"),
                {"type": "array", "items": _ref("InteractionContent")},
                {"type": "array", "items": _ref("InteractionStep")},
            ],
            "description": (
                "Input for an interaction: a prompt string, a single content "
                "object, a list of content objects, or a list of steps."
            ),
        },
        "InteractionContent": {
            "type": "object",
            "description": (
                "Typed content part of the interactions API. Discriminated by "
                "`type` (`text`, `image`, `audio`, `video`, `document`); this is "
                "an open union, so variant-specific fields beyond the common ones "
                "below are preserved as-is."
            ),
            "properties": {
                "type": {
                    "type": "string",
                    "description": "Content variant, e.g. `text` or `image`.",
                },
                "text": {
                    "type": "string",
                    "description": "Text payload (for `text` content).",
                },
                "data": {
                    "type": "string",
                    "description": "Base64-encoded payload (for media content).",
                },
                "mime_type": {
                    "type": "string",
                    "description": "MIME type of the payload.",
                },
                "uri": {
                    "type": "string",
                    "description": "URI of the payload when it is not inline.",
                },
                "annotations": {
                    "type": "array",
                    "description": "Annotations attached to the content.",
                    "items": {"type": "object", "additionalProperties": True},
                },
            },
            "additionalProperties": True,
        },
        "InteractionStep": {
            "type": "object",
            "description": (
                "A single execution step of an interaction. Discriminated by "
                "`type`; known step types include `user_input`, `thought`, "
                "`model_output`, `function_call`, `function_result`, "
                "`code_execution_call`, `code_execution_result`, "
                "`google_search_call`, `google_search_result`, "
                "`google_maps_call`, `google_maps_result`, `file_search_call`, "
                "`file_search_result`, `mcp_server_tool_call`, "
                "`mcp_server_tool_result`, `processing_call`, "
                "`processing_result`, `retrieval_call`, `retrieval_result`, "
                "`url_context_call`, and `url_context_result`. This is an open "
                "union, so step-specific fields are preserved as-is."
            ),
            "properties": {
                "type": {"type": "string", "description": "Step variant."},
                "content": {
                    "type": "array",
                    "items": _ref("InteractionContent"),
                    "description": "Content carried by the step, when applicable.",
                },
                "error": {
                    "type": "object",
                    "description": "Error status attached to the step.",
                    "additionalProperties": True,
                },
            },
            "additionalProperties": True,
        },
        "InteractionError": {
            "type": "object",
            "description": "Error message from an interaction.",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "A URI that identifies the error type.",
                },
                "message": {
                    "type": "string",
                    "description": "A human-readable error message.",
                },
            },
            "additionalProperties": False,
        },
        "InteractionUsage": {
            "type": "object",
            "description": "Statistics on the interaction request's token usage.",
            "properties": {
                "cached_tokens_by_modality": {
                    "type": "array",
                    "items": _ref("InteractionModalityTokens"),
                },
                "grounding_tool_count": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string"},
                            "count": {"type": "integer"},
                        },
                        "additionalProperties": False,
                    },
                },
                "input_tokens_by_modality": {
                    "type": "array",
                    "items": _ref("InteractionModalityTokens"),
                },
                "output_tokens_by_modality": {
                    "type": "array",
                    "items": _ref("InteractionModalityTokens"),
                },
                "tool_use_tokens_by_modality": {
                    "type": "array",
                    "items": _ref("InteractionModalityTokens"),
                },
            },
            "additionalProperties": False,
        },
        "InteractionModalityTokens": {
            "type": "object",
            "description": "Token count for one response modality.",
            "properties": {
                "modality": {
                    "type": "string",
                    "enum": ["text", "image", "audio", "video", "document"],
                },
                "tokens": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "InteractionSafetySetting": {
            "type": "object",
            "description": "Safety setting for an interaction.",
            "properties": {
                "type": {"type": "string", "description": "Harm category."},
                "threshold": {
                    "type": "string",
                    "description": "Blocking threshold for the category.",
                },
                "method": {
                    "type": "string",
                    "description": "Optional harm-blocking method.",
                },
            },
            "required": ["type", "threshold"],
            "additionalProperties": False,
        },
        "InteractionGenerationConfig": {
            "type": "object",
            "description": (
                "Generation config for model-backed interactions. Covers the "
                "documented top-level fields; nested configs (image, speech, "
                "video, transcription) follow the interactions wire format."
            ),
            "properties": {
                "max_output_tokens": {"type": "integer"},
                "seed": {"type": "integer"},
                "stop_sequences": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "temperature": {"type": "number"},
                "thinking_level": {"type": "string"},
                "thinking_summaries": {"type": "string"},
                "top_p": {"type": "number"},
            },
            "additionalProperties": True,
        },
        "InteractionEnvironment": {
            "type": "object",
            "description": (
                "Remote execution environment configuration for an agent or "
                "interaction."
            ),
            "properties": {
                "type": {"const": "remote"},
                "environment_id": {
                    "type": "string",
                    "description": "ID of an existing environment to reuse.",
                },
                "env": {
                    "oneOf": [
                        {
                            "type": "object",
                            "additionalProperties": {
                                "type": "object",
                                "properties": {
                                    "value": {"type": "string"},
                                    "credential": {"type": "string"},
                                },
                                "additionalProperties": False,
                            },
                        },
                        {"type": "string"},
                    ],
                    "description": (
                        "Environment variables: a map of name to value/credential "
                        "binding, or a serialized string."
                    ),
                },
                "network": {
                    "description": (
                        "Network egress configuration for the environment."
                    ),
                },
                "sources": {
                    "type": "array",
                    "items": _ref("EnvironmentSource"),
                    "description": "Sources mounted into the environment.",
                },
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "InteractionWebhookConfig": {
            "type": "object",
            "description": "Webhook delivery configuration for an interaction.",
            "properties": {
                "uris": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Webhook URIs that receive interaction events.",
                },
                "user_metadata": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Arbitrary metadata attached to deliveries.",
                },
            },
            "additionalProperties": False,
        },
        "CreateAgentInteraction": {
            "type": "object",
            "description": (
                "Request to create an agent-backed interaction. Exactly one of "
                "this shape or `CreateModelInteraction` is the body of "
                "`POST /v1beta/interactions`."
            ),
            "properties": {
                "agent": {
                    "type": "string",
                    "description": (
                        "Agent option to run, e.g. "
                        "`antigravity-preview-05-2026` or a Deep Research agent ID."
                    ),
                },
                "agent_config": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Agent configuration overrides.",
                },
                "background": {
                    "type": "boolean",
                    "description": "Run the interaction in the background.",
                },
                "environment": _ref("InteractionEnvironment"),
                "input": _ref("InteractionsInput"),
                "labels": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "previous_interaction_id": {"type": "string"},
                "response_format": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Structured output format.",
                },
                "response_mime_type": {"type": "string"},
                "response_modalities": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["text", "image", "audio", "video", "document"],
                    },
                },
                "safety_settings": {
                    "type": "array",
                    "items": _ref("InteractionSafetySetting"),
                },
                "service_tier": {
                    "type": "string",
                    "enum": ["flex", "standard", "priority", "deferred"],
                },
                "store": {
                    "type": "boolean",
                    "description": "Whether the interaction is persisted.",
                },
                "stream": {
                    "type": "boolean",
                    "description": (
                        "If true, the response is a server-sent event stream of "
                        "interaction events instead of a single JSON object."
                    ),
                },
                "system_instruction": {"type": "string"},
                "tools": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "webhook_config": _ref("InteractionWebhookConfig"),
            },
            "required": ["agent"],
            "additionalProperties": False,
        },
        "CreateModelInteraction": {
            "type": "object",
            "description": (
                "Request to create a model-backed interaction. Exactly one of "
                "this shape or `CreateAgentInteraction` is the body of "
                "`POST /v1beta/interactions`."
            ),
            "properties": {
                "model": {
                    "type": "string",
                    "description": "Model to run the interaction with.",
                },
                "background": {
                    "type": "boolean",
                    "description": "Run the interaction in the background.",
                },
                "cached_content": {"type": "string"},
                "environment": _ref("InteractionEnvironment"),
                "generation_config": _ref("InteractionGenerationConfig"),
                "input": _ref("InteractionsInput"),
                "labels": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
                "previous_interaction_id": {"type": "string"},
                "response_format": {
                    "type": "object",
                    "additionalProperties": True,
                    "description": "Structured output format.",
                },
                "response_mime_type": {"type": "string"},
                "response_modalities": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["text", "image", "audio", "video", "document"],
                    },
                },
                "safety_settings": {
                    "type": "array",
                    "items": _ref("InteractionSafetySetting"),
                },
                "service_tier": {
                    "type": "string",
                    "enum": ["flex", "standard", "priority", "deferred"],
                },
                "store": {
                    "type": "boolean",
                    "description": "Whether the interaction is persisted.",
                },
                "stream": {
                    "type": "boolean",
                    "description": (
                        "If true, the response is a server-sent event stream of "
                        "interaction events instead of a single JSON object."
                    ),
                },
                "system_instruction": {"type": "string"},
                "tools": {
                    "type": "array",
                    "items": {"type": "object", "additionalProperties": True},
                },
                "webhook_config": _ref("InteractionWebhookConfig"),
            },
            "required": ["model"],
            "additionalProperties": False,
        },
        "CreateInteractionRequest": {
            "oneOf": [
                _ref("CreateAgentInteraction"),
                _ref("CreateModelInteraction"),
            ],
            "description": (
                "Body of `POST /v1beta/interactions`: either an agent-backed or "
                "a model-backed interaction."
            ),
        },
        "Credential": {
            "type": "object",
            "description": (
                "Server-managed credential resource stored in Secret Manager. "
                "Fields are snake_case, matching the python-genai GAOS wire "
                "format. Secret values are input-only and never returned."
            ),
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Output only. Unique identifier for the credential.",
                },
                "type": {
                    "type": "string",
                    "enum": [
                        "bearer_token",
                        "oauth2",
                        "environment_variable",
                    ],
                    "description": "Output only. The type of credential.",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "revoked"],
                    "description": "Output only. Current status of the credential.",
                },
                "create_time": _ref("GoogleTimestamp"),
                "update_time": _ref("GoogleTimestamp"),
            },
            "additionalProperties": False,
        },
        "CredentialCreateRequest": {
            "oneOf": [
                _ref("HttpBearerCredentialConfig"),
                _ref("OAuth2CredentialConfig"),
                _ref("EnvironmentVariableCredentialConfig"),
            ],
            "description": (
                "Body of `POST /v1beta/credentials`, discriminated by `type`."
            ),
        },
        "CredentialUpdateRequest": {
            "oneOf": [
                _ref("HttpBearerCredentialUpdate"),
                _ref("OAuth2CredentialUpdate"),
                _ref("EnvironmentVariableCredentialUpdate"),
            ],
            "description": (
                "Body of `PATCH /v1beta/credentials/{id}`, discriminated by "
                "`type`. Same shapes as the create variants with every field "
                "optional."
            ),
        },
        "HttpBearerCredentialConfig": {
            "type": "object",
            "description": "HTTP Bearer token credential (create).",
            "properties": {
                "type": {"const": "bearer_token"},
                "id": {
                    "type": "string",
                    "description": "Identifier for the credential.",
                },
                "token": {
                    "type": "string",
                    "description": (
                        "Input only. The static bearer token. Write-only; never "
                        "returned in responses."
                    ),
                },
                "header_name": {
                    "type": "string",
                    "description": "Header name to inject the token into.",
                },
                "prefix": {
                    "type": "string",
                    "description": (
                        "Prefix prepended to the token. Defaults to `Bearer`."
                    ),
                },
            },
            "required": ["type", "id", "token"],
            "additionalProperties": False,
        },
        "HttpBearerCredentialUpdate": {
            "type": "object",
            "description": "HTTP Bearer token credential (update).",
            "properties": {
                "type": {"const": "bearer_token"},
                "token": {
                    "type": "string",
                    "description": "Input only. The static bearer token.",
                },
                "header_name": {"type": "string"},
                "prefix": {"type": "string"},
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "OAuth2CredentialConfig": {
            "type": "object",
            "description": "OAuth2 credential with automatic token refresh (create).",
            "properties": {
                "type": {"const": "oauth2"},
                "id": {
                    "type": "string",
                    "description": "Identifier for the credential.",
                },
                "client_id": {
                    "type": "string",
                    "description": "OAuth2 client ID.",
                },
                "client_secret": {
                    "type": "string",
                    "description": (
                        "Input only. OAuth2 client secret. Write-only; never "
                        "returned in responses."
                    ),
                },
                "refresh_token": {
                    "type": "string",
                    "description": (
                        "Input only. OAuth2 refresh token. Write-only; never "
                        "returned in responses."
                    ),
                },
                "token_url": {
                    "type": "string",
                    "description": "OAuth2 token endpoint URL for refreshing access tokens.",
                },
                "scopes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of OAuth2 scopes.",
                },
            },
            "required": ["type", "id", "client_id", "client_secret", "refresh_token", "token_url"],
            "additionalProperties": False,
        },
        "OAuth2CredentialUpdate": {
            "type": "object",
            "description": "OAuth2 credential with automatic token refresh (update).",
            "properties": {
                "type": {"const": "oauth2"},
                "client_id": {"type": "string"},
                "client_secret": {
                    "type": "string",
                    "description": "Input only. OAuth2 client secret.",
                },
                "refresh_token": {
                    "type": "string",
                    "description": "Input only. OAuth2 refresh token.",
                },
                "token_url": {"type": "string"},
                "scopes": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "EnvironmentVariableCredentialConfig": {
            "type": "object",
            "description": "Environment variable credential (create).",
            "properties": {
                "type": {"const": "environment_variable"},
                "id": {
                    "type": "string",
                    "description": "Identifier for the credential.",
                },
                "injection_location": {
                    "type": "string",
                    "enum": ["header", "query", "body"],
                    "description": "Locations where the value can be injected.",
                },
                "value": {
                    "type": "string",
                    "description": (
                        "Input only. Secret value of the environment variable. "
                        "Write-only; never returned in responses."
                    ),
                },
                "trusted_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Domains allowed to receive this environment variable."
                    ),
                },
            },
            "required": ["type", "id", "injection_location", "value"],
            "additionalProperties": False,
        },
        "EnvironmentVariableCredentialUpdate": {
            "type": "object",
            "description": "Environment variable credential (update).",
            "properties": {
                "type": {"const": "environment_variable"},
                "injection_location": {
                    "type": "string",
                    "enum": ["header", "query", "body"],
                },
                "value": {
                    "type": "string",
                    "description": "Input only. Secret value of the environment variable.",
                },
                "trusted_domains": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["type"],
            "additionalProperties": False,
        },
        "ListCredentialsResponse": {
            "type": "object",
            "description": "Response for listing credentials.",
            "properties": {
                "credentials": {
                    "type": "array",
                    "items": _ref("Credential"),
                },
                "next_page_token": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "Environment": {
            "type": "object",
            "description": (
                "An execution environment for an agent (Agent Platform). Fields "
                "are snake_case, matching the python-genai GAOS wire format."
            ),
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Output only. The ID of the environment.",
                },
                "created": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Output only. Creation time (ISO 8601).",
                },
                "updated": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Output only. Last update time (ISO 8601).",
                },
                "last_accessed": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Output only. Last access time (ISO 8601).",
                },
                "file_count": {
                    "type": "integer",
                    "description": "Output only. The number of files in the environment.",
                },
                "size_bytes": {
                    "type": "integer",
                    "format": "int64",
                    "description": "Output only. Total size of the environment files in bytes.",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "expired"],
                    "description": "Output only. The status of the environment container.",
                },
                "network": {
                    "description": "Network configuration for the environment.",
                },
            },
            "additionalProperties": False,
        },
        "CreateEnvironmentRequest": {
            "type": "object",
            "description": "Request for creating an environment.",
            "properties": {
                "from_environment": {
                    "type": "string",
                    "description": (
                        "The source environment to copy/fork from. When "
                        "specified, `sources` must be empty."
                    ),
                },
                "network": {
                    "oneOf": [
                        _ref("EnvironmentNetworkEgressAllowlist"),
                        {"type": "string", "enum": ["disabled"]},
                    ],
                    "description": "Network configuration for the environment.",
                },
                "sources": {
                    "type": "array",
                    "items": _ref("EnvironmentSource"),
                    "description": "Sources to be mounted into the environment.",
                },
            },
            "additionalProperties": False,
        },
        "EnvironmentNetworkEgressAllowlist": {
            "type": "object",
            "description": "Egress allowlist for an environment's network.",
            "properties": {
                "allowlist": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "domain": {
                                "type": "string",
                                "description": "Domain requests are allowed to.",
                            },
                            "credential": {
                                "type": "string",
                                "description": "Credential applied to the domain.",
                            },
                        },
                        "required": ["domain"],
                        "additionalProperties": False,
                    },
                }
            },
            "additionalProperties": False,
        },
        "EnvironmentSource": {
            "type": "object",
            "description": "A source mounted into an execution environment.",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["gcs", "inline", "repository", "skill_registry"],
                },
                "source": {
                    "type": "string",
                    "description": "Location of the source (e.g. GCS prefix).",
                },
                "target": {
                    "type": "string",
                    "description": "Mount path inside the environment.",
                },
                "content": {
                    "type": "string",
                    "description": "Inline content (for `inline` sources).",
                },
                "encoding": {
                    "type": "string",
                    "description": "Encoding of inline content.",
                },
            },
            "additionalProperties": False,
        },
        "ListEnvironmentsResponse": {
            "type": "object",
            "description": "Response for listing environments.",
            "properties": {
                "environments": {
                    "type": "array",
                    "items": _ref("Environment"),
                },
                "next_page_token": {
                    "type": "string",
                    "description": "Pagination token.",
                },
            },
            "additionalProperties": False,
        },
        "Trigger": {
            "type": "object",
            "description": (
                "A trigger configuration that is scheduled to run an agent. "
                "Fields are snake_case, matching the python-genai GAOS wire "
                "format."
            ),
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Output only. The ID of the trigger.",
                },
                "interaction": _ref("CreateAgentInteraction"),
                "schedule": {
                    "type": "string",
                    "description": "The cron schedule on which the trigger runs (standard cron format).",
                },
                "time_zone": {
                    "type": "string",
                    "description": "Time zone in which the schedule is interpreted.",
                },
                "display_name": {"type": "string"},
                "environment_id": {
                    "type": "string",
                    "description": "The environment ID for the trigger execution.",
                },
                "execution_timeout_seconds": {
                    "type": "integer",
                    "description": "The execution timeout for the triggered interaction.",
                },
                "max_consecutive_failures": {
                    "type": "integer",
                    "description": (
                        "Maximum consecutive failures allowed before the trigger "
                        "is automatically paused."
                    ),
                },
                "consecutive_failure_count": {
                    "type": "integer",
                    "description": "Output only. Consecutive failures since the last success.",
                },
                "status": {
                    "type": "string",
                    "enum": ["active", "paused", "error"],
                    "description": "Output only. The current status of the trigger.",
                },
                "previous_interaction_id": {
                    "type": "string",
                    "description": "Output only. ID of the last interaction created by this trigger.",
                },
                "create_time": _ref("GoogleTimestamp"),
                "update_time": _ref("GoogleTimestamp"),
                "last_run_time": _ref("GoogleTimestamp"),
                "next_run_time": _ref("GoogleTimestamp"),
                "last_pause_time": _ref("GoogleTimestamp"),
                "last_resume_time": _ref("GoogleTimestamp"),
            },
            "required": ["id", "interaction", "schedule", "time_zone"],
            "additionalProperties": False,
        },
        "TriggerCreateRequest": {
            "type": "object",
            "description": "Body of `POST /v1beta/triggers`.",
            "properties": {
                "interaction": _ref("CreateAgentInteraction"),
                "schedule": {
                    "type": "string",
                    "description": "The cron schedule on which the trigger should run.",
                },
                "time_zone": {
                    "type": "string",
                    "description": "Time zone in which the schedule should be interpreted.",
                },
                "display_name": {"type": "string"},
                "environment_id": {"type": "string"},
                "execution_timeout_seconds": {"type": "integer"},
                "max_consecutive_failures": {"type": "integer"},
            },
            "required": ["interaction", "schedule", "time_zone"],
            "additionalProperties": False,
        },
        "TriggerUpdateRequest": {
            "type": "object",
            "description": "Body of `PATCH /v1beta/triggers/{id}`.",
            "properties": {
                "display_name": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": ["active", "paused", "error"],
                },
            },
            "additionalProperties": False,
        },
        "TriggerExecution": {
            "type": "object",
            "description": "An execution instance of a trigger.",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Output only. The ID of the trigger execution.",
                },
                "trigger_id": {
                    "type": "string",
                    "description": "Output only. The ID of the trigger that created this execution.",
                },
                "status": {
                    "type": "string",
                    "enum": [
                        "in_progress",
                        "completed",
                        "failed",
                        "skipped",
                        "timed_out",
                    ],
                    "description": "Output only. The status of the execution.",
                },
                "environment_id": {
                    "type": "string",
                    "description": "Output only. The environment ID used for the execution.",
                },
                "interaction_id": {
                    "type": "string",
                    "description": "Output only. The ID of the interaction created by this execution.",
                },
                "error": {
                    "type": "string",
                    "description": "Output only. The error message if the execution failed.",
                },
                "scheduled_time": _ref("GoogleTimestamp"),
                "start_time": _ref("GoogleTimestamp"),
                "end_time": _ref("GoogleTimestamp"),
            },
            "required": ["id", "trigger_id"],
            "additionalProperties": False,
        },
        "ListTriggersResponse": {
            "type": "object",
            "description": "Response for listing triggers.",
            "properties": {
                "triggers": {"type": "array", "items": _ref("Trigger")},
                "next_page_token": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "ListTriggerExecutionsResponse": {
            "type": "object",
            "description": "Response for listing executions of a trigger.",
            "properties": {
                "trigger_executions": {
                    "type": "array",
                    "items": _ref("TriggerExecution"),
                },
                "next_page_token": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "Webhook": {
            "type": "object",
            "description": (
                "A webhook resource delivering event notifications. Fields are "
                "snake_case, matching the python-genai GAOS wire format."
            ),
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Output only. The ID of the webhook.",
                },
                "name": {
                    "type": "string",
                    "description": "The user-provided name of the webhook.",
                },
                "uri": {
                    "type": "string",
                    "description": "The URI to which webhook events are sent.",
                },
                "subscribed_events": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "batch.succeeded",
                            "batch.expired",
                            "batch.failed",
                            "interaction.requires_action",
                            "interaction.completed",
                            "interaction.failed",
                            "video.generated",
                        ],
                    },
                    "description": "The events that the webhook is subscribed to.",
                },
                "state": {
                    "type": "string",
                    "enum": [
                        "enabled",
                        "disabled",
                        "disabled_due_to_failed_deliveries",
                    ],
                    "description": "Output only. The state of the webhook.",
                },
                "new_signing_secret": {
                    "type": "string",
                    "description": (
                        "Output only. The new signing secret. Only populated on "
                        "create and rotate responses."
                    ),
                },
                "signing_secrets": {
                    "type": "array",
                    "items": _ref("WebhookSigningSecret"),
                    "description": "Output only. The signing secrets of the webhook.",
                },
                "create_time": _ref("GoogleTimestamp"),
                "update_time": _ref("GoogleTimestamp"),
            },
            "required": ["subscribed_events", "uri"],
            "additionalProperties": False,
        },
        "WebhookSigningSecret": {
            "type": "object",
            "description": (
                "A signing secret used to verify webhook payloads (truncated "
                "form; the full secret is only revealed once)."
            ),
            "properties": {
                "truncated_secret": {
                    "type": "string",
                    "description": "Output only. The truncated version of the signing secret.",
                },
                "expire_time": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Output only. The expiration date of the signing secret.",
                },
            },
            "additionalProperties": False,
        },
        "WebhookCreateRequest": {
            "type": "object",
            "description": "Body of `POST /v1beta/webhooks`.",
            "properties": {
                "subscribed_events": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "batch.succeeded",
                            "batch.expired",
                            "batch.failed",
                            "interaction.requires_action",
                            "interaction.completed",
                            "interaction.failed",
                            "video.generated",
                        ],
                    },
                },
                "uri": {
                    "type": "string",
                    "description": "The URI to which webhook events will be sent.",
                },
                "name": {
                    "type": "string",
                    "description": "The user-provided name of the webhook.",
                },
            },
            "required": ["subscribed_events", "uri"],
            "additionalProperties": False,
        },
        "WebhookUpdateRequest": {
            "type": "object",
            "description": "Body of `PATCH /v1beta/webhooks/{id}`.",
            "properties": {
                "name": {"type": "string"},
                "uri": {"type": "string"},
                "state": {
                    "type": "string",
                    "enum": [
                        "enabled",
                        "disabled",
                        "disabled_due_to_failed_deliveries",
                    ],
                },
                "subscribed_events": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": [
                            "batch.succeeded",
                            "batch.expired",
                            "batch.failed",
                            "interaction.requires_action",
                            "interaction.completed",
                            "interaction.failed",
                            "video.generated",
                        ],
                    },
                },
            },
            "additionalProperties": False,
        },
        "RotateSigningSecretRequest": {
            "type": "object",
            "description": "Body of webhook signing-secret rotation.",
            "properties": {
                "revocation_behavior": {
                    "type": "string",
                    "enum": [
                        "revoke_previous_secrets_after_h24",
                        "revoke_previous_secrets_immediately",
                    ],
                    "description": "The revocation behavior for previous signing secrets.",
                },
            },
            "additionalProperties": False,
        },
        "WebhookRotateSigningSecretResponse": {
            "type": "object",
            "description": "Response for webhook signing-secret rotation.",
            "properties": {
                "secret": {
                    "type": "string",
                    "description": "Output only. The newly generated signing secret.",
                },
            },
            "additionalProperties": False,
        },
        "ListWebhooksResponse": {
            "type": "object",
            "description": "Response for listing webhooks.",
            "properties": {
                "webhooks": {"type": "array", "items": _ref("Webhook")},
                "next_page_token": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "CountTokensRequest": {
            "type": "object",
            "properties": {
                "contents": {
                    "type": "array",
                    "items": _ref("Content"),
                },
                "generateContentRequest": _ref("GenerateContentRequest"),
            },
            "additionalProperties": False,
        },
        "CountTokensResponse": {
            "type": "object",
            "properties": {
                "totalTokens": {"type": "integer"},
                "cachedContentTokenCount": {"type": "integer"},
                "promptTokensDetails": {
                    "type": "array",
                    "items": _ref("ModalityTokenCount"),
                },
                "cacheTokensDetails": {
                    "type": "array",
                    "items": _ref("ModalityTokenCount"),
                },
            },
            "additionalProperties": False,
        },
        "PredictRequest": {
            "type": "object",
            "properties": {
                "instances": {
                    "type": "array",
                    "items": _ref("GoogleProtobufValue"),
                },
                "parameters": _ref("GoogleProtobufValue"),
            },
            "required": ["instances"],
            "additionalProperties": False,
        },
        "PredictResponse": {
            "type": "object",
            "properties": {
                "predictions": {
                    "type": "array",
                    "items": _ref("GoogleProtobufValue"),
                },
            },
            "additionalProperties": False,
        },
        "ListFilesResponse": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": _ref("File"),
                },
                "nextPageToken": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "RegisterFilesRequest": {
            "type": "object",
            "properties": {
                "uris": {
                    "type": "array",
                    "items": {"type": "string"},
                }
            },
            "required": ["uris"],
            "additionalProperties": False,
        },
        "RegisterFilesResponse": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "items": _ref("File"),
                }
            },
            "additionalProperties": False,
        },
        "CachedContentUsageMetadata": {
            "type": "object",
            "properties": {
                "totalTokenCount": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "CachedContent": {
            "type": "object",
            "properties": {
                "contents": {
                    "type": "array",
                    "items": _ref("Content"),
                },
                "tools": {
                    "type": "array",
                    "items": _ref("Tool"),
                },
                "createTime": _ref("GoogleTimestamp"),
                "updateTime": _ref("GoogleTimestamp"),
                "usageMetadata": _ref("CachedContentUsageMetadata"),
                "expireTime": _ref("GoogleTimestamp"),
                "ttl": _ref("GoogleDuration"),
                "name": {"type": "string"},
                "displayName": {"type": "string"},
                "model": {"type": "string"},
                "systemInstruction": _ref("Content"),
                "toolConfig": _ref("ToolConfig"),
            },
            "additionalProperties": False,
        },
        "CachedContentPatchRequest": {
            "type": "object",
            "properties": {
                "ttl": _ref("GoogleDuration"),
                "expireTime": _ref("GoogleTimestamp"),
            },
            "additionalProperties": False,
        },
        "ListCachedContentsResponse": {
            "type": "object",
            "properties": {
                "cachedContents": {
                    "type": "array",
                    "items": _ref("CachedContent"),
                },
                "nextPageToken": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "EmptyObject": {
            "type": "object",
            "additionalProperties": False,
        },
    }


def _gaos_pagination_parameters(filter_: bool = False) -> list[dict]:
    """Query parameters shared by Agent Platform (GAOS) list operations.

    The GAOS surface serializes snake_case query parameters, unlike the
    proto-JSON endpoints which use pageSize/pageToken.
    """
    parameters = [
        {
            "name": "page_size",
            "in": "query",
            "required": False,
            "schema": {"type": "integer"},
            "description": "Maximum number of items to return per page.",
        },
        {
            "name": "page_token",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": "Pagination token from a previous list call.",
        },
    ]
    if filter_:
        parameters.insert(
            0,
            {
                "name": "filter",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
                "description": "Filter expression (e.g., by state).",
            },
        )
    return parameters


def _gaos_update_mask_parameter() -> dict:
    return {
        "name": "update_mask",
        "in": "query",
        "required": False,
        "schema": {"type": "string"},
        "description": "Optional list of fields to update.",
    }


def _gaos_environment_files_query_parameters() -> list[dict]:
    return [
        {
            "name": "page_size",
            "in": "query",
            "required": False,
            "schema": {"type": "integer"},
            "description": "Maximum number of entries to return per page (for directory listing).",
        },
        {
            "name": "page_token",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": "Pagination token for directory listing.",
        },
        {
            "name": "recursive",
            "in": "query",
            "required": False,
            "schema": {"type": "boolean"},
            "description": "If true and the path is a directory, recursively lists all files.",
        },
    ]


def _annotate_gaos_resource_id(path_item: dict, collection: str) -> None:
    """Rewrite the fallback description of GAOS `{id}` path parameters.

    The all-methods index lists these bindings as plain `{id}` templates
    without a `resource/*` pattern, so the generic builder falls back to
    "Google API path binding". Give them the same guidance as the
    pattern-derived parameters.
    """
    for parameter in path_item.get("parameters", []):
        if parameter.get("name") == "id" and parameter.get("in") == "path":
            parameter["description"] = (
                f"ID within the `{collection}` collection. Pass just the "
                f"resource ID, not the full resource name."
            )
            break


def apply_native_operation_overrides(operation, path_item: dict) -> tuple[dict, list[tuple[str, dict]]]:
    """Returns the updated path item and any extra path items to materialize."""

    request_ref = None
    response_ref = None
    extra_parameters: list[dict] = []
    extra_paths: list[tuple[str, dict]] = []
    needs_upload_alias = False
    needs_file_search_upload_alias = False
    needs_generated_file_download_path = False
    needs_stream_generate_content_sse = False

    key = (operation.resource, operation.name, operation.method, operation.raw_path)

    if key == ("v1beta.models", "generateContent", "POST", "/v1beta/{model=models/*}:generateContent"):
        request_ref = "GenerateContentRequest"
        response_ref = "GenerateContentResponse"
    elif key == ("v1beta.models", "embedContent", "POST", "/v1beta/{model=models/*}:embedContent"):
        request_ref = "EmbedContentRequest"
        response_ref = "EmbedContentResponse"
    elif key == ("v1beta.batches", "list", "GET", "/v1beta/{name=batches}"):
        response_ref = "ListBatchesResponse"
        extra_parameters.extend(
            [
                {
                    "name": "filter",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
                {
                    "name": "pageSize",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer"},
                },
                {
                    "name": "pageToken",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
                {
                    "name": "returnPartialSuccess",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "boolean"},
                },
            ]
        )
    elif key == ("v1beta.batches", "delete", "DELETE", "/v1beta/{name=batches/*}"):
        response_ref = "EmptyObject"
    elif key == ("v1beta.batches", "get", "GET", "/v1beta/{name=batches/*}"):
        response_ref = "BatchOperation"
    elif key == ("v1beta.batches", "cancel", "POST", "/v1beta/{name=batches/*}:cancel"):
        response_ref = "EmptyObject"
    elif key == (
        "v1beta.models",
        "asyncBatchEmbedContent",
        "POST",
        "/v1beta/{batch.model=models/*}:asyncBatchEmbedContent",
    ):
        request_ref = "CreateBatchEmbedContentRequest"
        response_ref = "BatchOperation"
    elif key == (
        "v1beta.models",
        "batchGenerateContent",
        "POST",
        "/v1beta/{batch.model=models/*}:batchGenerateContent",
    ):
        request_ref = "CreateBatchGenerateContentRequest"
        response_ref = "BatchOperation"
    elif key == (
        "v1beta.batches",
        "updateEmbedContentBatch",
        "PATCH",
        "/v1beta/{embedContentBatch.name=batches/*}:updateEmbedContentBatch",
    ):
        request_ref = "EmbedContentBatch"
        response_ref = "EmbedContentBatch"
        extra_parameters.append(
            {
                "name": "updateMask",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
            }
        )
    elif key == (
        "v1beta.batches",
        "updateGenerateContentBatch",
        "PATCH",
        "/v1beta/{generateContentBatch.name=batches/*}:updateGenerateContentBatch",
    ):
        request_ref = "GenerateContentBatch"
        response_ref = "GenerateContentBatch"
        extra_parameters.append(
            {
                "name": "updateMask",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
            }
        )
    elif key == ("v1beta.fileSearchStores", "create", "POST", "/v1beta/fileSearchStores"):
        request_ref = "CreateFileSearchStoreRequest"
        response_ref = "FileSearchStore"
    elif key == ("v1beta.fileSearchStores", "delete", "DELETE", "/v1beta/{name=fileSearchStores/*}"):
        response_ref = "EmptyObject"
        extra_parameters.append(
            {
                "name": "force",
                "in": "query",
                "required": False,
                "schema": {"type": "boolean"},
            }
        )
    elif key == ("v1beta.fileSearchStores", "get", "GET", "/v1beta/{name=fileSearchStores/*}"):
        response_ref = "FileSearchStore"
    elif key == ("v1beta.fileSearchStores", "list", "GET", "/v1beta/fileSearchStores"):
        response_ref = "ListFileSearchStoresResponse"
        extra_parameters.extend(
            [
                {
                    "name": "pageSize",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer"},
                },
                {
                    "name": "pageToken",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
            ]
        )
    elif key == (
        "v1beta.fileSearchStores",
        "importFile",
        "POST",
        "/v1beta/{fileSearchStoreName=fileSearchStores/*}:importFile",
    ):
        request_ref = "ImportFileRequest"
        response_ref = "LongRunningOperation"
    elif key == (
        "v1beta.files",
        "uploadToFileSearchStore",
        "POST",
        "/v1beta/{fileSearchStoreName=fileSearchStores/*}:uploadToFileSearchStore",
    ):
        request_ref = "UploadToFileSearchStoreMetadataRequest"
        response_ref = "LongRunningOperation"
        needs_file_search_upload_alias = True
    elif key == (
        "v1beta.auth_tokens",
        "create",
        "POST",
        "/v1beta/auth_tokens",
    ):
        request_ref = "CreateAuthTokenRequest"
        response_ref = "AuthToken"
    elif key == (
        "v1beta.files",
        "download",
        "GET",
        "/v1beta/{parent=environments/*}/files",
    ):
        path_item["description"] = (
            "Retrieves a file or directory from a Code Execution environment "
            "snapshot. Google SDKs address a specific file by appending its "
            "relative path as a trailing path segment "
            "(`/v1beta/environments/{environment}/files/{path}`); the all-methods "
            "reference documents the collection URL only."
        )
        response_ref = "GetEnvironmentFilesResponse"
        extra_parameters.extend(
            [
                {
                    "name": "page_size",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer"},
                    "description": "Maximum number of entries to return per page (for directory listing).",
                },
                {
                    "name": "page_token",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                    "description": "Pagination token for directory listing.",
                },
                {
                    "name": "recursive",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "boolean"},
                    "description": "If true and the path is a directory, recursively lists all files.",
                },
            ]
        )
    elif key == (
        "v1beta.fileSearchStores.operations",
        "get",
        "GET",
        "/v1beta/{name=fileSearchStores/*/operations/*}",
    ):
        response_ref = "LongRunningOperation"
    elif key == (
        "v1beta.fileSearchStores.upload.operations",
        "get",
        "GET",
        "/v1beta/{name=fileSearchStores/*/upload/operations/*}",
    ):
        response_ref = "LongRunningOperation"
    elif key == ("v1beta.models", "get", "GET", "/v1beta/{name=models/*}"):
        response_ref = "Model"
    elif key == ("v1beta.models", "list", "GET", "/v1beta/models"):
        response_ref = "ListModelsResponse"
        extra_parameters.extend(
            [
                {
                    "name": "pageSize",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer"},
                },
                {
                    "name": "pageToken",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
            ]
        )
    elif key == (
        "v1beta.models",
        "countTokens",
        "POST",
        "/v1beta/{model=models/*}:countTokens",
    ):
        request_ref = "CountTokensRequest"
        response_ref = "CountTokensResponse"
    elif key == (
        "v1beta.models",
        "batchEmbedContents",
        "POST",
        "/v1beta/{model=models/*}:batchEmbedContents",
    ):
        request_ref = "BatchEmbedContentsRequest"
        response_ref = "BatchEmbedContentsResponse"
    elif key == (
        "v1beta.models",
        "predict",
        "POST",
        "/v1beta/{model=models/*}:predict",
    ):
        request_ref = "PredictRequest"
        response_ref = "PredictResponse"
    elif key == (
        "v1beta.models",
        "predictLongRunning",
        "POST",
        "/v1beta/{model=models/*}:predictLongRunning",
    ):
        request_ref = "PredictRequest"
        response_ref = "LongRunningOperation"
    elif key == (
        "v1beta.models",
        "streamGenerateContent",
        "POST",
        "/v1beta/{model=models/*}:streamGenerateContent",
    ):
        request_ref = "GenerateContentRequest"
        needs_stream_generate_content_sse = True
    elif key == (
        "v1beta.fileSearchStores.documents",
        "delete",
        "DELETE",
        "/v1beta/{name=fileSearchStores/*/documents/*}",
    ):
        response_ref = "EmptyObject"
        extra_parameters.append(
            {
                "name": "force",
                "in": "query",
                "required": False,
                "schema": {"type": "boolean"},
            }
        )
    elif key == (
        "v1beta.fileSearchStores.documents",
        "get",
        "GET",
        "/v1beta/{name=fileSearchStores/*/documents/*}",
    ):
        response_ref = "Document"
    elif key == (
        "v1beta.fileSearchStores.documents",
        "list",
        "GET",
        "/v1beta/{parent=fileSearchStores/*}/documents",
    ):
        response_ref = "ListDocumentsResponse"
        extra_parameters.extend(
            [
                {
                    "name": "pageSize",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer"},
                },
                {
                    "name": "pageToken",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
            ]
        )
    elif key == ("v1beta.cachedContents", "create", "POST", "/v1beta/cachedContents"):
        request_ref = "CachedContent"
        response_ref = "CachedContent"
    elif key == ("v1beta.cachedContents", "get", "GET", "/v1beta/{name=cachedContents/*}"):
        response_ref = "CachedContent"
    elif key == ("v1beta.cachedContents", "list", "GET", "/v1beta/cachedContents"):
        response_ref = "ListCachedContentsResponse"
        extra_parameters.extend(
            [
                {
                    "name": "pageSize",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer"},
                },
                {
                    "name": "pageToken",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
            ]
        )
    elif key == ("v1beta.cachedContents", "patch", "PATCH", "/v1beta/{cachedContent.name=cachedContents/*}"):
        request_ref = "CachedContentPatchRequest"
        response_ref = "CachedContent"
        extra_parameters.append(
            {
                "name": "updateMask",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
            }
        )
    elif key == ("v1beta.cachedContents", "delete", "DELETE", "/v1beta/{name=cachedContents/*}"):
        response_ref = "EmptyObject"
    elif key == ("v1beta.files", "upload", "POST", "/v1beta/files"):
        request_ref = "CreateFileRequest"
        response_ref = "MediaUploadResponse"
        needs_upload_alias = True
    elif key == ("v1beta.files", "get", "GET", "/v1beta/{name=files/*}"):
        response_ref = "File"
        needs_generated_file_download_path = True
    elif key == ("v1beta.files", "list", "GET", "/v1beta/files"):
        response_ref = "ListFilesResponse"
        extra_parameters.extend(
            [
                {
                    "name": "pageSize",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "integer"},
                },
                {
                    "name": "pageToken",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
            ]
        )
    elif key == ("v1beta.files", "delete", "DELETE", "/v1beta/{name=files/*}"):
        response_ref = "EmptyObject"
    elif key == ("v1beta.files", "register", "POST", "/v1beta/files:register"):
        request_ref = "RegisterFilesRequest"
        response_ref = "RegisterFilesResponse"
    elif key == ("v1beta.agents", "ListAgents", "GET", "/v1beta/agents"):
        response_ref = "ListAgentsResponse"
        extra_parameters.extend(_gaos_pagination_parameters())
    elif key == ("v1beta.agents", "CreateAgent", "POST", "/v1beta/agents"):
        request_ref = "Agent"
        response_ref = "Agent"
    elif key == ("v1beta.agents", "GetAgent", "GET", "/v1beta/agents/{id}"):
        response_ref = "Agent"
        _annotate_gaos_resource_id(path_item, collection="agents")
    elif key == ("v1beta.agents", "DeleteAgent", "DELETE", "/v1beta/agents/{id}"):
        response_ref = "EmptyObject"
        _annotate_gaos_resource_id(path_item, collection="agents")
    elif key == ("v1beta.interactions", "CreateInteraction", "POST", "/v1beta/interactions"):
        request_ref = "CreateInteractionRequest"
        response_ref = "Interaction"
        path_item["description"] = (
            "Creates a new interaction with either an agent or a model. When the "
            "body sets `stream: true`, the response is a server-sent event "
            "stream of interaction events rather than a single JSON object."
        )
    elif key == ("v1beta.interactions", "getInteractionById", "GET", "/v1beta/interactions/{id}"):
        response_ref = "Interaction"
        _annotate_gaos_resource_id(path_item, collection="interactions")
    elif key == ("v1beta.interactions", "deleteInteraction", "DELETE", "/v1beta/interactions/{id}"):
        response_ref = "EmptyObject"
        _annotate_gaos_resource_id(path_item, collection="interactions")
    elif key == (
        "v1beta.interactions",
        "cancelInteractionById",
        "POST",
        "/v1beta/interactions/{id}/cancel",
    ):
        response_ref = "Interaction"
        _annotate_gaos_resource_id(path_item, collection="interactions")
    elif key == ("v1beta.interactions", "CreateCredential", "POST", "/v1beta/credentials"):
        request_ref = "CredentialCreateRequest"
        response_ref = "Credential"
    elif key == ("v1beta.interactions", "ListCredentials", "GET", "/v1beta/credentials"):
        response_ref = "ListCredentialsResponse"
        extra_parameters.extend(_gaos_pagination_parameters())
    elif key == ("v1beta.interactions", "GetCredential", "GET", "/v1beta/credentials/{id}"):
        response_ref = "Credential"
        _annotate_gaos_resource_id(path_item, collection="credentials")
    elif key == ("v1beta.interactions", "UpdateCredential", "PATCH", "/v1beta/credentials/{id}"):
        request_ref = "CredentialUpdateRequest"
        response_ref = "Credential"
        _annotate_gaos_resource_id(path_item, collection="credentials")
    elif key == ("v1beta.interactions", "DeleteCredential", "DELETE", "/v1beta/credentials/{id}"):
        response_ref = "EmptyObject"
        _annotate_gaos_resource_id(path_item, collection="credentials")
    elif key == ("v1beta.environments", "ListEnvironments", "GET", "/v1beta/environments"):
        response_ref = "ListEnvironmentsResponse"
        extra_parameters.extend(_gaos_pagination_parameters())
    elif key == ("v1beta.environments", "CreateEnvironment", "POST", "/v1beta/environments"):
        request_ref = "CreateEnvironmentRequest"
        response_ref = "Environment"
    elif key == ("v1beta.environments", "GetEnvironment", "GET", "/v1beta/environments/{id}"):
        response_ref = "Environment"
        _annotate_gaos_resource_id(path_item, collection="environments")
    elif key == ("v1beta.environments", "DeleteEnvironment", "DELETE", "/v1beta/environments/{id}"):
        response_ref = "EmptyObject"
        _annotate_gaos_resource_id(path_item, collection="environments")
    elif key == (
        "v1beta.environments",
        "GetEnvironmentFiles",
        "GET",
        "/v1beta/environments/{environment}/files/{path}",
    ):
        response_ref = "GetEnvironmentFilesResponse"
        for parameter in path_item.get("parameters", []):
            if parameter.get("name") == "environment":
                parameter["description"] = (
                    "ID within the `environments` collection. Pass just the "
                    "resource ID, not the full resource name."
                )
            elif parameter.get("name") == "path":
                parameter["description"] = (
                    "Relative path of the file or directory within the "
                    "environment snapshot."
                )
        extra_parameters.extend(_gaos_environment_files_query_parameters())
    elif key == ("v1beta.triggers", "ListTriggers", "GET", "/v1beta/triggers"):
        response_ref = "ListTriggersResponse"
        extra_parameters.extend(_gaos_pagination_parameters(filter_=True))
    elif key == ("v1beta.triggers", "CreateTrigger", "POST", "/v1beta/triggers"):
        request_ref = "TriggerCreateRequest"
        response_ref = "Trigger"
    elif key == ("v1beta.triggers", "GetTrigger", "GET", "/v1beta/triggers/{id}"):
        response_ref = "Trigger"
        _annotate_gaos_resource_id(path_item, collection="triggers")
    elif key == ("v1beta.triggers", "UpdateTrigger", "PATCH", "/v1beta/triggers/{id}"):
        request_ref = "TriggerUpdateRequest"
        response_ref = "Trigger"
        _annotate_gaos_resource_id(path_item, collection="triggers")
        extra_parameters.append(_gaos_update_mask_parameter())
    elif key == ("v1beta.triggers", "DeleteTrigger", "DELETE", "/v1beta/triggers/{id}"):
        response_ref = "EmptyObject"
        _annotate_gaos_resource_id(path_item, collection="triggers")
    elif key == ("v1beta.triggers", "RunTrigger", "POST", "/v1beta/triggers/{trigger_id}/executions"):
        response_ref = "TriggerExecution"
        for parameter in path_item.get("parameters", []):
            if parameter.get("name") == "trigger_id":
                parameter["description"] = (
                    "ID within the `triggers` collection. Pass just the "
                    "resource ID, not the full resource name."
                )
    elif key == (
        "v1beta.triggers",
        "ListTriggerExecutions",
        "GET",
        "/v1beta/triggers/{trigger_id}/executions",
    ):
        response_ref = "ListTriggerExecutionsResponse"
        for parameter in path_item.get("parameters", []):
            if parameter.get("name") == "trigger_id":
                parameter["description"] = (
                    "ID within the `triggers` collection. Pass just the "
                    "resource ID, not the full resource name."
                )
        extra_parameters.extend(_gaos_pagination_parameters())
    elif key == ("v1beta.webhooks", "ListWebhooks", "GET", "/v1beta/webhooks"):
        response_ref = "ListWebhooksResponse"
        extra_parameters.extend(_gaos_pagination_parameters())
    elif key == ("v1beta.webhooks", "CreateWebhook", "POST", "/v1beta/webhooks"):
        request_ref = "WebhookCreateRequest"
        response_ref = "Webhook"
    elif key == ("v1beta.webhooks", "GetWebhook", "GET", "/v1beta/webhooks/{id}"):
        response_ref = "Webhook"
        _annotate_gaos_resource_id(path_item, collection="webhooks")
    elif key == ("v1beta.webhooks", "UpdateWebhook", "PATCH", "/v1beta/webhooks/{id}"):
        request_ref = "WebhookUpdateRequest"
        response_ref = "Webhook"
        _annotate_gaos_resource_id(path_item, collection="webhooks")
        extra_parameters.append(_gaos_update_mask_parameter())
    elif key == ("v1beta.webhooks", "DeleteWebhook", "DELETE", "/v1beta/webhooks/{id}"):
        response_ref = "EmptyObject"
        _annotate_gaos_resource_id(path_item, collection="webhooks")
    elif key == ("v1beta.webhooks", "PingWebhook", "POST", "/v1beta/webhooks/{id}:ping"):
        response_ref = "EmptyObject"
        _annotate_gaos_resource_id(path_item, collection="webhooks")
        path_item["description"] = (
            "Sends a ping event to a webhook. The response body is empty; "
            "delivery confirmation arrives asynchronously at the webhook URI."
        )
    elif key == (
        "v1beta.webhooks",
        "RotateSigningSecret",
        "POST",
        "/v1beta/webhooks/{id}:rotateSigningSecret",
    ):
        request_ref = "RotateSigningSecretRequest"
        response_ref = "WebhookRotateSigningSecretResponse"
        _annotate_gaos_resource_id(path_item, collection="webhooks")

    if request_ref:
        path_item["requestBody"] = {
            "required": operation.method in {"POST", "PATCH"},
            "content": {
                "application/json": {"schema": _ref(request_ref)},
            },
        }
        if key == ("v1beta.files", "upload", "POST", "/v1beta/files"):
            path_item["requestBody"]["required"] = False

    if response_ref:
        path_item["responses"] = {
            "200": {
                "description": "Successful response",
                "content": {
                    "application/json": {"schema": _ref(response_ref)},
                },
            }
        }

    if extra_parameters:
        path_item["parameters"] = [*path_item.get("parameters", []), *extra_parameters]

    if key == ("v1beta.batches", "cancel", "POST", "/v1beta/{name=batches/*}:cancel"):
        path_item.pop("requestBody", None)

    if key in {
        (
            "v1beta.interactions",
            "cancelInteractionById",
            "POST",
            "/v1beta/interactions/{id}/cancel",
        ),
        ("v1beta.triggers", "RunTrigger", "POST", "/v1beta/triggers/{trigger_id}/executions"),
        ("v1beta.webhooks", "PingWebhook", "POST", "/v1beta/webhooks/{id}:ping"),
    }:
        path_item.pop("requestBody", None)

    if needs_stream_generate_content_sse:
        path_item["x-gemini-doc-source"] = "https://ai.google.dev/api/generate-content"
        path_item["x-gemini-stream-event-schema"] = _ref("GenerateContentResponse")
        path_item["parameters"] = [
            *path_item.get("parameters", []),
            {
                "name": "alt",
                "in": "query",
                "required": True,
                "schema": {"type": "string", "enum": ["sse"]},
                "description": "Required streaming mode documented for streamGenerateContent.",
            },
        ]
        path_item["responses"] = {
            "200": {
                "description": "Successful server-sent event stream of GenerateContentResponse chunks",
                "content": {
                    "text/event-stream": {
                        "schema": {"type": "string"},
                    }
                },
            }
        }

    if needs_upload_alias:
        upload_variant = deepcopy(path_item)
        upload_variant["x-google-original-path"] = "/upload/v1beta/files"
        upload_variant["x-gemini-doc-source"] = "https://ai.google.dev/gemini-api/docs/files"
        upload_variant["operationId"] = f"{upload_variant['operationId']}_mediaUpload"
        upload_variant["requestBody"] = {
            "required": False,
            "description": (
                "Google requires multipart/related or resumable upload "
                "protocol. The content types shown here are a simplified "
                "representation. See the Gemini Files API guide for the "
                "actual upload flow."
            ),
            "content": {
                "application/json": {"schema": _ref("CreateFileRequest")},
                "application/octet-stream": {
                    "schema": {"type": "string", "format": "binary"}
                },
            },
        }
        extra_paths.append(("/upload/v1beta/files", upload_variant))

    if needs_file_search_upload_alias:
        upload_variant = deepcopy(path_item)
        upload_variant["operationId"] = f"{upload_variant['operationId']}_mediaUpload"
        upload_variant["x-google-original-path"] = (
            "/upload/v1beta/{fileSearchStoreName=fileSearchStores/*}:uploadToFileSearchStore"
        )
        upload_variant["x-gemini-doc-source"] = (
            "https://ai.google.dev/api/file-search/file-search-stores"
        )
        upload_variant["requestBody"] = {
            "required": False,
            "description": (
                "Google requires multipart/related or resumable upload "
                "protocol. The content types shown here are a simplified "
                "representation. See the Gemini Files API guide for the "
                "actual upload flow."
            ),
            "content": {
                "application/json": {
                    "schema": _ref("UploadToFileSearchStoreMetadataRequest")
                },
                "application/octet-stream": {
                    "schema": {"type": "string", "format": "binary"}
                },
            },
        }
        extra_paths.append(
            (
                "/upload/v1beta/fileSearchStores/{fileSearchStore}:uploadToFileSearchStore",
                upload_variant,
            )
        )

    if needs_generated_file_download_path:
        download_variant = deepcopy(path_item)
        download_variant["operationId"] = f"{download_variant['operationId']}_mediaDownload"
        download_variant["summary"] = "download"
        download_variant["description"] = (
            "Downloads generated file bytes. Officially documented in the Gemini Batch API "
            "guide for batch result files."
        )
        download_variant["x-google-original-path"] = "/download/v1beta/files/{file}:download"
        download_variant["x-gemini-doc-source"] = "https://ai.google.dev/gemini-api/docs/batch-api"
        download_variant["parameters"] = [
            *download_variant.get("parameters", []),
            {
                "name": "alt",
                "in": "query",
                "required": True,
                "schema": {"type": "string", "enum": ["media"]},
                "description": "Required media download mode documented in the Batch API guide.",
            },
        ]
        download_variant["responses"] = {
            "200": {
                "description": "Successful media download",
                "content": {
                    "application/octet-stream": {
                        "schema": {"type": "string", "format": "binary"}
                    }
                },
            }
        }
        download_variant.pop("requestBody", None)
        extra_paths.append(("/download/v1beta/files/{file}:download", download_variant))

    return path_item, extra_paths


def selected_native_operation_keys() -> set[tuple[str, str]]:
    return {
        ("GET", "/v1beta/models"),
        ("GET", "/v1beta/models/{model}"),
        ("POST", "/v1beta/models/{model}:countTokens"),
        ("POST", "/v1beta/models/{model}:batchEmbedContents"),
        ("POST", "/v1beta/models/{model}:predict"),
        ("POST", "/v1beta/models/{model}:predictLongRunning"),
        ("POST", "/v1beta/models/{model}:generateContent"),
        ("POST", "/v1beta/models/{model}:streamGenerateContent"),
        ("POST", "/v1beta/models/{model}:embedContent"),
        ("GET", "/v1beta/batches"),
        ("GET", "/v1beta/batches/{batch}"),
        ("DELETE", "/v1beta/batches/{batch}"),
        ("POST", "/v1beta/batches/{batch}:cancel"),
        ("PATCH", "/v1beta/batches/{batch}:updateEmbedContentBatch"),
        ("PATCH", "/v1beta/batches/{batch}:updateGenerateContentBatch"),
        ("POST", "/v1beta/models/{model}:asyncBatchEmbedContent"),
        ("POST", "/v1beta/models/{model}:batchGenerateContent"),
        ("POST", "/v1beta/auth_tokens"),
        ("POST", "/v1beta/fileSearchStores"),
        ("GET", "/v1beta/fileSearchStores"),
        ("GET", "/v1beta/fileSearchStores/{fileSearchStore}"),
        ("DELETE", "/v1beta/fileSearchStores/{fileSearchStore}"),
        ("POST", "/v1beta/fileSearchStores/{fileSearchStore}:importFile"),
        ("POST", "/v1beta/fileSearchStores/{fileSearchStore}:uploadToFileSearchStore"),
        ("POST", "/upload/v1beta/fileSearchStores/{fileSearchStore}:uploadToFileSearchStore"),
        ("GET", "/v1beta/environments/{environment}/files"),
        ("GET", "/v1beta/fileSearchStores/{fileSearchStore}/documents"),
        ("GET", "/v1beta/fileSearchStores/{fileSearchStore}/documents/{document}"),
        ("DELETE", "/v1beta/fileSearchStores/{fileSearchStore}/documents/{document}"),
        ("POST", "/v1beta/cachedContents"),
        ("GET", "/v1beta/cachedContents"),
        ("GET", "/v1beta/cachedContents/{cachedContent}"),
        ("PATCH", "/v1beta/cachedContents/{cachedContent}"),
        ("DELETE", "/v1beta/cachedContents/{cachedContent}"),
        ("POST", "/v1beta/files"),
        ("POST", "/upload/v1beta/files"),
        ("GET", "/download/v1beta/files/{file}:download"),
        ("GET", "/v1beta/files"),
        ("GET", "/v1beta/files/{file}"),
        ("DELETE", "/v1beta/files/{file}"),
        ("POST", "/v1beta/files:register"),
        ("GET", "/v1beta/agents"),
        ("POST", "/v1beta/agents"),
        ("GET", "/v1beta/agents/{id}"),
        ("DELETE", "/v1beta/agents/{id}"),
        ("POST", "/v1beta/interactions"),
        ("GET", "/v1beta/interactions/{id}"),
        ("DELETE", "/v1beta/interactions/{id}"),
        ("POST", "/v1beta/interactions/{id}/cancel"),
        ("GET", "/v1beta/credentials"),
        ("POST", "/v1beta/credentials"),
        ("GET", "/v1beta/credentials/{id}"),
        ("PATCH", "/v1beta/credentials/{id}"),
        ("DELETE", "/v1beta/credentials/{id}"),
        ("GET", "/v1beta/environments"),
        ("POST", "/v1beta/environments"),
        ("GET", "/v1beta/environments/{id}"),
        ("DELETE", "/v1beta/environments/{id}"),
        ("GET", "/v1beta/environments/{environment}/files/{path}"),
        ("GET", "/v1beta/triggers"),
        ("POST", "/v1beta/triggers"),
        ("GET", "/v1beta/triggers/{id}"),
        ("PATCH", "/v1beta/triggers/{id}"),
        ("DELETE", "/v1beta/triggers/{id}"),
        ("GET", "/v1beta/triggers/{trigger_id}/executions"),
        ("POST", "/v1beta/triggers/{trigger_id}/executions"),
        ("GET", "/v1beta/webhooks"),
        ("POST", "/v1beta/webhooks"),
        ("GET", "/v1beta/webhooks/{id}"),
        ("PATCH", "/v1beta/webhooks/{id}"),
        ("DELETE", "/v1beta/webhooks/{id}"),
        ("POST", "/v1beta/webhooks/{id}:ping"),
        ("POST", "/v1beta/webhooks/{id}:rotateSigningSecret"),
    }
