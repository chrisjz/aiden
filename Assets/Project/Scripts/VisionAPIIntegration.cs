using System;
using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;
using CandyCoded.env;

public class VisionAPIIntegration : MonoBehaviour
{
    public Camera cameraToCapture;
    public TMP_Text responseText;
    public Button sendButton;
    public bool saveInput = false;

    private string apiURL;

    private void Start()
    {
        // Check if Vision API is enabled
        env.TryParseEnvironmentVariable("VISION_ENABLE", out bool isEnabled);
        if (!isEnabled)
        {
            Debug.Log("Vision API is disabled");
            return;
        }
        else
        {
            Debug.Log("Vision API is enabled");
        }

        // Set API URL from environment variables to point to the occipital endpoint
        if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/occipital";
            Debug.Log($"Brain API URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for brain API URL.");
            return;
        }

        sendButton.onClick.AddListener(SendRequestToVisionAPI);
    }

    private void SendRequestToVisionAPI()
    {
        if (cameraToCapture == null || cameraToCapture.targetTexture == null)
        {
            Debug.LogError("Camera or its target texture is not assigned.");
            return;
        }

        Texture2D capturedImage = CaptureCameraRenderTexture();
        string base64Image = TextureToBase64(capturedImage);

        // Save the captured image to a file
        if (saveInput)
        {
            SaveImageToFile(capturedImage);
        }

        Debug.Log("Start vision inference.");
        StartCoroutine(StreamRequest(base64Image));
    }

    private IEnumerator StreamRequest(string base64Image)
    {
        var json = JsonUtility.ToJson(new VisionRequest { image = base64Image });
        var request = new UnityWebRequest(apiURL, "POST")
        {
            uploadHandler = new UploadHandlerRaw(System.Text.Encoding.UTF8.GetBytes(json)),
            downloadHandler = new DownloadHandlerBuffer()
        };
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)
        {
            string responseString = request.downloadHandler.text;
            Debug.Log("Response: " + responseString);
            UpdateResponseText(responseString);
        }
        else
        {
            Debug.LogError("Error: " + request.error);
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

    private void SaveImageToFile(Texture2D texture)
    {
        byte[] imageBytes = texture.EncodeToPNG();
        string directoryPath = Path.Combine(Application.dataPath, "../Temp/CapturedSenses/Vision");

        // Ensure directory exists
        if (!Directory.Exists(directoryPath))
        {
            Directory.CreateDirectory(directoryPath);
        }

        string timestamp = DateTime.Now.ToString("yyyyMMddHHmmssffff");
        string filePath = Path.Combine(directoryPath, $"capturedImage_{timestamp}.png");

        File.WriteAllBytes(filePath, imageBytes);
        Debug.Log($"Saved captured image to {filePath}");
    }
}

// Define classes to match the JSON structure of the response
[Serializable]
public class VisionRequest
{
    public string image;
}
