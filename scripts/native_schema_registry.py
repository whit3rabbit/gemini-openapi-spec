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
        "TextPrompt": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
            "additionalProperties": False,
        },
        "LegacyMessage": {
            "type": "object",
            "properties": {
                "author": {"type": "string"},
                "content": {"type": "string"},
                "citationMetadata": _ref("CitationMetadata"),
            },
            "required": ["content"],
            "additionalProperties": False,
        },
        "LegacyExample": {
            "type": "object",
            "properties": {
                "input": _ref("LegacyMessage"),
                "output": _ref("LegacyMessage"),
            },
            "required": ["input", "output"],
            "additionalProperties": False,
        },
        "MessagePrompt": {
            "type": "object",
            "properties": {
                "context": {"type": "string"},
                "examples": {
                    "type": "array",
                    "items": _ref("LegacyExample"),
                },
                "messages": {
                    "type": "array",
                    "items": _ref("LegacyMessage"),
                },
            },
            "required": ["messages"],
            "additionalProperties": False,
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
        "CreateTunedModelOperation": {
            "type": "object",
            "description": "Long-running operation returned by tunedModels.create with typed metadata and response.",
            "properties": {
                "name": {"type": "string"},
                "done": {"type": "boolean"},
                "error": _ref("JobError"),
                "metadata": _ref("CreateTunedModelMetadata"),
                "response": _ref("TunedModel"),
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
        "LegacyTokenCountResponse": {
            "type": "object",
            "properties": {
                "tokenCount": {"type": "integer"},
            },
            "additionalProperties": False,
        },
        "CountTextTokensRequest": {
            "type": "object",
            "properties": {
                "prompt": _ref("TextPrompt"),
            },
            "required": ["prompt"],
            "additionalProperties": False,
        },
        "CountMessageTokensRequest": {
            "type": "object",
            "properties": {
                "prompt": _ref("MessagePrompt"),
            },
            "required": ["prompt"],
            "additionalProperties": False,
        },
        "Embedding": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "array",
                    "items": {"type": "number"},
                }
            },
            "additionalProperties": False,
        },
        "BlockedReason": {
            "type": "string",
            "enum": [
                "BLOCKED_REASON_UNSPECIFIED",
                "SAFETY",
                "OTHER",
            ],
        },
        "ContentFilter": {
            "type": "object",
            "properties": {
                "reason": _ref("BlockedReason"),
                "message": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "SafetyFeedback": {
            "type": "object",
            "properties": {
                "rating": _ref("SafetyRating"),
                "setting": _ref("SafetySetting"),
            },
            "additionalProperties": False,
        },
        "TextCompletion": {
            "type": "object",
            "properties": {
                "output": {"type": "string"},
                "safetyRatings": {
                    "type": "array",
                    "items": _ref("SafetyRating"),
                },
                "citationMetadata": _ref("CitationMetadata"),
            },
            "additionalProperties": False,
        },
        "GenerateTextRequest": {
            "type": "object",
            "properties": {
                "prompt": _ref("TextPrompt"),
                "safetySettings": {
                    "type": "array",
                    "items": _ref("SafetySetting"),
                },
                "stopSequences": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 5,
                },
                "temperature": {"type": "number"},
                "candidateCount": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 8,
                },
                "maxOutputTokens": {"type": "integer"},
                "topP": {"type": "number"},
                "topK": {"type": "integer"},
            },
            "required": ["prompt"],
            "additionalProperties": False,
        },
        "GenerateTextResponse": {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": _ref("TextCompletion"),
                },
                "filters": {
                    "type": "array",
                    "items": _ref("ContentFilter"),
                },
                "safetyFeedback": {
                    "type": "array",
                    "items": _ref("SafetyFeedback"),
                },
            },
            "additionalProperties": False,
        },
        "GenerateMessageRequest": {
            "type": "object",
            "properties": {
                "prompt": _ref("MessagePrompt"),
                "temperature": {"type": "number"},
                "candidateCount": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 8,
                },
                "topP": {"type": "number"},
                "topK": {"type": "integer"},
            },
            "required": ["prompt"],
            "additionalProperties": False,
        },
        "GenerateMessageResponse": {
            "type": "object",
            "properties": {
                "candidates": {
                    "type": "array",
                    "items": _ref("LegacyMessage"),
                },
                "messages": {
                    "type": "array",
                    "items": _ref("LegacyMessage"),
                },
                "filters": {
                    "type": "array",
                    "items": _ref("ContentFilter"),
                },
            },
            "additionalProperties": False,
        },
        "EmbedTextRequest": {
            "type": "object",
            "properties": {
                "model": {"type": "string"},
                "text": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "EmbedTextResponse": {
            "type": "object",
            "properties": {
                "embedding": _ref("Embedding"),
            },
            "additionalProperties": False,
        },
        "BatchEmbedTextRequest": {
            "type": "object",
            "properties": {
                "texts": {
                    "type": "array",
                    "items": {"type": "string"},
                    "maxItems": 100,
                },
                "requests": {
                    "type": "array",
                    "items": _ref("EmbedTextRequest"),
                },
            },
            "additionalProperties": False,
        },
        "BatchEmbedTextResponse": {
            "type": "object",
            "properties": {
                "embeddings": {
                    "type": "array",
                    "items": _ref("Embedding"),
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
        "TuningExample": {
            "type": "object",
            "description": "A single example for tuning.",
            "properties": {
                "textInput": {"type": "string"},
                "output": {"type": "string"},
            },
            "required": ["output"],
            "additionalProperties": False,
        },
        "TuningExamples": {
            "type": "object",
            "description": "A set of tuning examples. Can be training or validation data.",
            "properties": {
                "examples": {
                    "type": "array",
                    "items": _ref("TuningExample"),
                },
            },
            "additionalProperties": False,
        },
        "Dataset": {
            "type": "object",
            "description": "Dataset for training or validation.",
            "properties": {
                "examples": _ref("TuningExamples"),
            },
            "additionalProperties": False,
        },
        "Hyperparameters": {
            "type": "object",
            "description": "Hyperparameters controlling the tuning process.",
            "properties": {
                "epochCount": {"type": "integer"},
                "batchSize": {"type": "integer"},
                "learningRate": {"type": "number"},
                "learningRateMultiplier": {"type": "number"},
            },
            "additionalProperties": False,
        },
        "TuningSnapshot": {
            "type": "object",
            "description": "Record for a single tuning step.",
            "properties": {
                "step": {"type": "integer"},
                "epoch": {"type": "integer"},
                "meanLoss": {"type": "number"},
                "computeTime": _ref("GoogleTimestamp"),
            },
            "additionalProperties": False,
        },
        "TuningTask": {
            "type": "object",
            "description": "Tuning tasks that create tuned models.",
            "properties": {
                "startTime": _ref("GoogleTimestamp"),
                "completeTime": _ref("GoogleTimestamp"),
                "snapshots": {
                    "type": "array",
                    "items": _ref("TuningSnapshot"),
                },
                "trainingData": _ref("Dataset"),
                "hyperparameters": _ref("Hyperparameters"),
            },
            "required": ["trainingData"],
            "additionalProperties": False,
        },
        "TunedModelSource": {
            "type": "object",
            "description": "Tuned model as a source for training a new model.",
            "properties": {
                "tunedModel": {"type": "string"},
                "baseModel": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "TunedModel": {
            "type": "object",
            "description": "A fine-tuned model created using CreateTunedModel.",
            "properties": {
                "name": {"type": "string"},
                "displayName": {"type": "string"},
                "description": {"type": "string"},
                "state": {
                    "type": "string",
                    "enum": ["STATE_UNSPECIFIED", "CREATING", "ACTIVE", "FAILED"],
                },
                "createTime": _ref("GoogleTimestamp"),
                "updateTime": _ref("GoogleTimestamp"),
                "tuningTask": _ref("TuningTask"),
                "baseModel": {"type": "string"},
                "temperature": {"type": "number"},
                "topP": {"type": "number"},
                "topK": {"type": "integer"},
                "tunedModelSource": _ref("TunedModelSource"),
                "readerProjectNumbers": {
                    "type": "array",
                    "items": {"type": "string"},
                },
            },
            "required": ["tuningTask"],
            "additionalProperties": False,
        },
        "CreateTunedModelMetadata": {
            "type": "object",
            "description": "Metadata about the state and progress of creating a tuned model.",
            "properties": {
                "tunedModel": {"type": "string"},
                "totalSteps": {"type": "integer"},
                "completedSteps": {"type": "integer"},
                "completedPercent": {"type": "number"},
                "snapshots": {
                    "type": "array",
                    "items": _ref("TuningSnapshot"),
                },
            },
            "additionalProperties": False,
        },
        "ListTunedModelsResponse": {
            "type": "object",
            "properties": {
                "tunedModels": {
                    "type": "array",
                    "items": _ref("TunedModel"),
                },
                "nextPageToken": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "Permission": {
            "type": "object",
            "description": (
                "Permission resource grants user, group or the rest of the world access "
                "to a tuned model."
            ),
            "properties": {
                "name": {"type": "string"},
                "granteeType": {
                    "type": "string",
                    "enum": [
                        "GRANTEE_TYPE_UNSPECIFIED",
                        "USER",
                        "GROUP",
                        "EVERYONE",
                    ],
                },
                "emailAddress": {"type": "string"},
                "role": {
                    "type": "string",
                    "enum": ["ROLE_UNSPECIFIED", "OWNER", "WRITER", "READER"],
                },
            },
            "required": ["role"],
            "additionalProperties": False,
        },
        "ListPermissionsResponse": {
            "type": "object",
            "properties": {
                "permissions": {
                    "type": "array",
                    "items": _ref("Permission"),
                },
                "nextPageToken": {"type": "string"},
            },
            "additionalProperties": False,
        },
        "TransferOwnershipRequest": {
            "type": "object",
            "description": "Request to transfer the ownership of the tuned model.",
            "properties": {
                "emailAddress": {"type": "string"},
            },
            "required": ["emailAddress"],
            "additionalProperties": False,
        },
        "TransferOwnershipResponse": {
            "type": "object",
            "description": "Response from TransferOwnership.",
            "additionalProperties": False,
        },
        "EmptyObject": {
            "type": "object",
            "additionalProperties": False,
        },
    }


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
        "countMessageTokens",
        "POST",
        "/v1beta/{model=models/*}:countMessageTokens",
    ):
        request_ref = "CountMessageTokensRequest"
        response_ref = "LegacyTokenCountResponse"
    elif key == (
        "v1beta.models",
        "countTextTokens",
        "POST",
        "/v1beta/{model=models/*}:countTextTokens",
    ):
        request_ref = "CountTextTokensRequest"
        response_ref = "LegacyTokenCountResponse"
    elif key == (
        "v1beta.models",
        "embedText",
        "POST",
        "/v1beta/{model=models/*}:embedText",
    ):
        request_ref = "EmbedTextRequest"
        response_ref = "EmbedTextResponse"
    elif key == (
        "v1beta.models",
        "batchEmbedText",
        "POST",
        "/v1beta/{model=models/*}:batchEmbedText",
    ):
        request_ref = "BatchEmbedTextRequest"
        response_ref = "BatchEmbedTextResponse"
    elif key == (
        "v1beta.models",
        "generateMessage",
        "POST",
        "/v1beta/{model=models/*}:generateMessage",
    ):
        request_ref = "GenerateMessageRequest"
        response_ref = "GenerateMessageResponse"
    elif key == (
        "v1beta.models",
        "generateText",
        "POST",
        "/v1beta/{model=models/*}:generateText",
    ):
        request_ref = "GenerateTextRequest"
        response_ref = "GenerateTextResponse"
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
    # -- tunedModels endpoints --
    elif key == ("v1beta.tunedModels", "create", "POST", "/v1beta/tunedModels"):
        request_ref = "TunedModel"
        response_ref = "CreateTunedModelOperation"
        extra_parameters.append(
            {
                "name": "tunedModelId",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
                "description": "Optional unique ID for the tuned model. If not set, one is generated.",
            }
        )
    elif key == ("v1beta.tunedModels", "list", "GET", "/v1beta/tunedModels"):
        response_ref = "ListTunedModelsResponse"
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
                {
                    "name": "filter",
                    "in": "query",
                    "required": False,
                    "schema": {"type": "string"},
                },
            ]
        )
    elif key == ("v1beta.tunedModels", "get", "GET", "/v1beta/{name=tunedModels/*}"):
        response_ref = "TunedModel"
    elif key == ("v1beta.tunedModels", "patch", "PATCH", "/v1beta/{tunedModel.name=tunedModels/*}"):
        request_ref = "TunedModel"
        response_ref = "TunedModel"
        extra_parameters.append(
            {
                "name": "updateMask",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
            }
        )
    elif key == ("v1beta.tunedModels", "delete", "DELETE", "/v1beta/{name=tunedModels/*}"):
        response_ref = "EmptyObject"
    elif key == (
        "v1beta.tunedModels",
        "generateContent",
        "POST",
        "/v1beta/{model=tunedModels/*}:generateContent",
    ):
        request_ref = "GenerateContentRequest"
        response_ref = "GenerateContentResponse"
    elif key == (
        "v1beta.tunedModels",
        "streamGenerateContent",
        "POST",
        "/v1beta/{model=tunedModels/*}:streamGenerateContent",
    ):
        request_ref = "GenerateContentRequest"
        needs_stream_generate_content_sse = True
    elif key == (
        "v1beta.tunedModels.permissions",
        "transferOwnership",
        "POST",
        "/v1beta/{name=tunedModels/*}:transferOwnership",
    ):
        request_ref = "TransferOwnershipRequest"
        response_ref = "TransferOwnershipResponse"
    # -- tunedModels.permissions endpoints --
    elif key == (
        "v1beta.tunedModels.permissions",
        "create",
        "POST",
        "/v1beta/{parent=tunedModels/*}/permissions",
    ):
        request_ref = "Permission"
        response_ref = "Permission"
    elif key == (
        "v1beta.tunedModels.permissions",
        "list",
        "GET",
        "/v1beta/{parent=tunedModels/*}/permissions",
    ):
        response_ref = "ListPermissionsResponse"
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
        "v1beta.tunedModels.permissions",
        "get",
        "GET",
        "/v1beta/{name=tunedModels/*/permissions/*}",
    ):
        response_ref = "Permission"
    elif key == (
        "v1beta.tunedModels.permissions",
        "patch",
        "PATCH",
        "/v1beta/{permission.name=tunedModels/*/permissions/*}",
    ):
        request_ref = "Permission"
        response_ref = "Permission"
        extra_parameters.append(
            {
                "name": "updateMask",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
            }
        )
    elif key == (
        "v1beta.tunedModels.permissions",
        "delete",
        "DELETE",
        "/v1beta/{name=tunedModels/*/permissions/*}",
    ):
        response_ref = "EmptyObject"

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
        ("POST", "/v1beta/models/{model}:countMessageTokens"),
        ("POST", "/v1beta/models/{model}:countTextTokens"),
        ("POST", "/v1beta/models/{model}:embedText"),
        ("POST", "/v1beta/models/{model}:batchEmbedText"),
        ("POST", "/v1beta/models/{model}:generateMessage"),
        ("POST", "/v1beta/models/{model}:generateText"),
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
        ("POST", "/v1beta/fileSearchStores"),
        ("GET", "/v1beta/fileSearchStores"),
        ("GET", "/v1beta/fileSearchStores/{fileSearchStore}"),
        ("DELETE", "/v1beta/fileSearchStores/{fileSearchStore}"),
        ("POST", "/v1beta/fileSearchStores/{fileSearchStore}:importFile"),
        ("POST", "/v1beta/fileSearchStores/{fileSearchStore}:uploadToFileSearchStore"),
        ("POST", "/upload/v1beta/fileSearchStores/{fileSearchStore}:uploadToFileSearchStore"),
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
        # tunedModels
        ("POST", "/v1beta/tunedModels"),
        ("GET", "/v1beta/tunedModels"),
        ("GET", "/v1beta/tunedModels/{tunedModel}"),
        ("PATCH", "/v1beta/tunedModels/{tunedModel}"),
        ("DELETE", "/v1beta/tunedModels/{tunedModel}"),
        ("POST", "/v1beta/tunedModels/{tunedModel}:generateContent"),
        ("POST", "/v1beta/tunedModels/{tunedModel}:streamGenerateContent"),
        ("POST", "/v1beta/tunedModels/{tunedModel}:transferOwnership"),
        # tunedModels.permissions
        ("POST", "/v1beta/tunedModels/{tunedModel}/permissions"),
        ("GET", "/v1beta/tunedModels/{tunedModel}/permissions"),
        ("GET", "/v1beta/tunedModels/{tunedModel}/permissions/{permission}"),
        ("PATCH", "/v1beta/tunedModels/{tunedModel}/permissions/{permission}"),
        ("DELETE", "/v1beta/tunedModels/{tunedModel}/permissions/{permission}"),
    }
