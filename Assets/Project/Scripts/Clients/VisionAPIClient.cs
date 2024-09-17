using System;
using System.Collections;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;
using CandyCoded.env;

public class VisionAPIClient
{
    private string apiURL;
    private Camera cameraCapture;
    private bool saveCapturedImage;

    public VisionAPIClient(Camera camera, bool saveInput = false)
    {
        // Check if Vision API is enabled
        env.TryParseEnvironmentVariable("VISION_ENABLE", out bool isEnabled);
        if (!isEnabled)
        {
            Debug.Log("Vision API is disabled");
            return;
        }

        // Set API URL from environment variables to point to the occipital endpoint
        if (env.TryParseEnvironmentVariable("BRAIN_API_PROTOCOL", out string protocol) &&
            env.TryParseEnvironmentVariable("BRAIN_API_HOST", out string host) &&
            env.TryParseEnvironmentVariable("BRAIN_API_PORT", out string port))
        {
            apiURL = $"{protocol}://{host}:{port}/occipital/";
            Debug.Log($"Occipital endpoint URL set to: {apiURL}");
        }
        else
        {
            Debug.LogError("Missing environment variables for brain API URL.");
        }

        // Assign the camera
        cameraCapture = camera;
        if (cameraCapture == null)
        {
            Debug.LogError("No camera was passed to VisionAPIClient.");
            return;
        }

        // Toggle saving captured image
        saveCapturedImage = saveInput;
    }

    public bool IsAPIEnabled()
    {
        return !string.IsNullOrEmpty(apiURL);
    }

    public IEnumerator GetVisionDataCoroutine(System.Action<string> onSuccess, System.Action<string> onError)
    {
        if (string.IsNullOrEmpty(apiURL))
        {
            onError?.Invoke("Vision API URL is not set.");
            yield break;
        }

        Texture2D capturedImage = CaptureCameraRenderTexture(cameraCapture);
        string base64Image = TextureToBase64(capturedImage);

        // Save the captured image to a file
        SaveImageToFile(capturedImage, saveCapturedImage);

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
            string response = request.downloadHandler.text;
            Debug.Log($"Vision API response: {response}");
            onSuccess?.Invoke(response);
        }
        else
        {
            onError?.Invoke("Vision API request failed: " + request.error);
        }
    }

    public Texture2D CaptureCameraRenderTexture(Camera cameraCapture)
    {
        if (cameraCapture == null || cameraCapture.targetTexture == null)
        {
            Debug.LogError("Camera or its target texture is not assigned.");
            return null;
        }

        RenderTexture currentRT = RenderTexture.active;
        RenderTexture.active = cameraCapture.targetTexture;

        cameraCapture.Render();

        Texture2D image = new Texture2D(cameraCapture.targetTexture.width, cameraCapture.targetTexture.height);
        image.ReadPixels(new Rect(0, 0, cameraCapture.targetTexture.width, cameraCapture.targetTexture.height), 0, 0);
        image.Apply();

        RenderTexture.active = currentRT;

        return image;
    }

    public string TextureToBase64(Texture2D texture)
    {
        if (texture == null)
        {
            Debug.LogError("Texture is null, cannot convert to base64.");
            return null;
        }

        byte[] imageBytes = texture.EncodeToPNG();
        return Convert.ToBase64String(imageBytes);
    }

    public void SaveImageToFile(Texture2D texture, bool saveInput)
    {
        if (!saveInput || texture == null) return;

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

    public IEnumerator SendRequestToVisionAPI(string base64Image, Action<string> onResponse)
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
            onResponse?.Invoke(responseString);
        }
        else
        {
            Debug.LogError("Error: " + request.error);
            onResponse?.Invoke(null);
        }
    }
}

// Define classes to match the JSON structure of the request
[Serializable]
public class VisionRequest
{
    public string image;
}
