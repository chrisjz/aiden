using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;
using CandyCoded.env;

public class CognitiveAPIUIController : MonoBehaviour
{
    public TMP_InputField playerInputField;
    public TMP_Text responseText;
    public Button sendButton;

    private string apiURL;
    private string modelName;

    private void Start()
    {
        // Set API URL from environment variables
        if (env.TryParseEnvironmentVariable("COGNITIVE_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("COGNITIVE_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("COGNITIVE_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/api/chat";
            Debug.Log($"Cognitive API URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for Cognitive API URL.");
            return;
        }

        // Set model name from environment variable
        if (env.TryParseEnvironmentVariable("COGNITIVE_MODEL", out modelName))
        {
            Debug.Log($"Using cognitive model: {modelName}");
        }
        else
        {
            Debug.LogError("Could not find cognitive model.");
            return;
        }

        sendButton.onClick.AddListener(SendMessageToAIden);
    }

    private void SendMessageToAIden()
    {
        string playerMessage = playerInputField.text;
        responseText.text = "";
        sendButton.interactable = false;

        Debug.Log("Start cognitive inference.");
        StartCoroutine(StreamRequest(playerMessage));
    }

    private IEnumerator StreamRequest(string message)
    {
        string formattedMessage = message.Replace("\n", "\\n"); // Replace newlines with \n escape sequence
        var json = $"{{\"model\": \"{modelName}\", \"messages\": [{{\"role\": \"user\", \"content\": \"{formattedMessage}\"}}]}}";
        var request = new UnityWebRequest(apiURL, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        request.SendWebRequest();

        int lastProcessedPosition = 0;
        while (!request.isDone)
        {
            if (request.downloadHandler.data != null)
            {
                string fullResponse = System.Text.Encoding.UTF8.GetString(request.downloadHandler.data);
                string newResponse = fullResponse.Substring(lastProcessedPosition);
                lastProcessedPosition = fullResponse.Length;

                string[] messages = newResponse.Split('\n');
                foreach (string messageJson in messages)
                {
                    if (!string.IsNullOrWhiteSpace(messageJson))
                    {
                        var responseObject = JsonUtility.FromJson<Response>(messageJson);
                        if (responseObject != null && responseObject.message != null)
                        {
                            UpdateResponseText(responseObject.message.content);
                        }
                    }
                }
            }
            yield return null;
        }

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError(request.error);
        }

        sendButton.interactable = true;
    }

    private void UpdateResponseText(string text)
    {
        // Trim leading space for just the first word
        if (responseText.text == "")
        {
            string trimmedText = text.TrimStart();
            responseText.text += trimmedText;
        }
        else
        {
            responseText.text += text;
        }
    }
}

// Define classes to match the JSON structure of the response
[Serializable]
public class Response
{
    public string model;
    public string created_at;
    public Message message;
    public bool done;
}

[Serializable]
public class Message
{
    public string role;
    public string content;
}
