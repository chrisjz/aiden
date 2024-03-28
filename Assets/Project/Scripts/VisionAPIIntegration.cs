using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;
using CandyCoded.env;

public class VisionAPIIntegration : MonoBehaviour
{
    public Camera cameraToCapture;
    public TMP_InputField promptInputField;
    public TMP_Text responseText;
    public Button sendButton;

    private string apiURL = "http://localhost:11435/api/generate";

    private void Start()
    {
        sendButton.onClick.AddListener(SendRequestToVisionAPI);
    }

    private void SendRequestToVisionAPI()
    {
        if (cameraToCapture == null || cameraToCapture.targetTexture == null)
        {
            Debug.LogError("Camera or its target texture is not assigned.");
            return;
        }

        string prompt = "What do you see?";
        Texture2D capturedImage = CaptureCameraRenderTexture();
        string base64Image = TextureToBase64(capturedImage);

        if (env.TryParseEnvironmentVariable("MODEL_VISION", out string modelName))
        {
            Debug.Log($"Using vision model: {modelName}");
        }
        else
        {
            Debug.LogError("Could not find vision model.");
        }

        StartCoroutine(StreamRequest(prompt, modelName, base64Image));
    }

    private IEnumerator StreamRequest(string prompt, string modelName, string base64Image)
    {
        var json = $"{{\"model\": \"{modelName}\", \"prompt\": \"{prompt}\", \"images\": [\"{base64Image}\"]}}";
        var request = new UnityWebRequest(apiURL, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = (UploadHandler)new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");
        request.SendWebRequest();

        int lastProcessedPosition = 0;
        string fullResponseText = "";
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
                        var responseObject = JsonUtility.FromJson<VisionResponse>(messageJson);
                        if (responseObject != null && responseObject.response != null)
                        {
                            fullResponseText += responseObject.response;
                        }
                    }
                }
            }
            yield return null;
        }

        UpdateResponseText(fullResponseText.Trim());

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError(request.error);
        }
    }


    private void UpdateResponseText(string text)
    {
        responseText.text = text;
    }

    private Texture2D CaptureCameraRenderTexture()
    {
        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = cameraToCapture.targetTexture;

        cameraToCapture.Render();

        Texture2D image = new Texture2D(cameraToCapture.targetTexture.width, cameraToCapture.targetTexture.height);
        image.ReadPixels(new Rect(0, 0, cameraToCapture.targetTexture.width, cameraToCapture.targetTexture.height), 0, 0);
        image.Apply();

        RenderTexture.active = currentRT;

        return image;
    }

    private string TextureToBase64(Texture2D texture)
    {
        byte[] imageBytes = texture.EncodeToPNG();
        return Convert.ToBase64String(imageBytes);
    }
}

// Define classes to match the JSON structure of the response
[Serializable]
public class VisionResponse
{
    public string model;
    public string created_at;
    public string response;
    public bool done;
}