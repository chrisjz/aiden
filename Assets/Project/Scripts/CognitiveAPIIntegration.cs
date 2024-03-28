using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;
using CandyCoded.env;

public class CognitiveAPIIntegration : MonoBehaviour
{
    public TMP_InputField playerInputField;
    public TMP_Text responseText;
    public Button sendButton;

    private string apiURL = "http://localhost:11434/api/chat";

    private void Start()
    {
        sendButton.onClick.AddListener(SendMessageToAIden);
    }

    private void SendMessageToAIden()
    {
        string playerMessage = playerInputField.text;
        responseText.text = "";

        if (env.TryParseEnvironmentVariable("MODEL_COGNITIVE", out string modelName))
        {
            Debug.Log($"Using cognitive model: {modelName}");
        }
        else
        {
            Debug.LogError("Could not find cognitive model.");
        }
        StartCoroutine(StreamRequest(playerMessage, modelName));
    }

    private IEnumerator StreamRequest(string message, string modelName)
    {
        var json = $"{{\"model\": \"{modelName}\", \"messages\": [{{\"role\": \"user\", \"content\": \"{message}\"}}]}}";
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
    }

    private void UpdateResponseText(string text)
    {
        string trimmedText = text.Trim();
        responseText.text += trimmedText + " ";
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
