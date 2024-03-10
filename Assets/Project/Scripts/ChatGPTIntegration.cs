using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;
using CandyCoded.env;


public class ChatGPTIntegration : MonoBehaviour
{
    public TMP_InputField playerInputField;
    public TMP_Text responseText;
    public Button sendButton;

    private string apiURL = "https://api.openai.com/v1/chat/completions";

    private void Start()
    {
        sendButton.onClick.AddListener(SendMessageToAIden);
    }

    private void SendMessageToAIden()
    {
        string playerMessage = playerInputField.text;
        StartCoroutine(PostRequest(playerMessage));
    }

    private IEnumerator PostRequest(string message)
    {
        var json = $"{{\"model\": \"gpt-3.5-turbo\", \"messages\": [{{\"role\": \"user\", \"content\": \"{message}\"}}]}}";
        var request = new UnityWebRequest(apiURL, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        if (env.TryParseEnvironmentVariable("OPENAI_API_KEY", out string apiKey))
        {
            Debug.Log($"Using ChatGPT API key: {apiKey}");
            request.SetRequestHeader("Authorization", "Bearer " + apiKey);
        }
        else
        {
            Debug.LogError("Could not find ChatGPT API key.");
        }

        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError(request.error);
        }
        else
        {
            string response = request.downloadHandler.text;
            // Extract the response text from the JSON response
            string responseText = ExtractResponseText(response);
            Debug.Log(responseText);
            UpdateResponseText(responseText);
        }
    }

    private string ExtractResponseText(string jsonResponse)
    {
        var responseObject = JsonUtility.FromJson<Response>(jsonResponse);
        if (responseObject.choices != null && responseObject.choices.Length > 0)
        {
            return responseObject.choices[0].message.content;
        }
        return "No response found.";
    }

    private void UpdateResponseText(string text)
    {
        responseText.text = text;
    }
}

// Define classes to match the JSON structure of the response
[Serializable]
public class Response
{
    public Choice[] choices;
}

[Serializable]
public class Choice
{
    public Message message;
}

[Serializable]
public class Message
{
    public string content;
}