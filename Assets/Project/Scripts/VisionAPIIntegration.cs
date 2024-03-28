using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;

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

        string prompt = promptInputField.text;
        Texture2D capturedImage = CaptureCameraRenderTexture();
        string base64Image = TextureToBase64(capturedImage);
        StartCoroutine(PostRequest(prompt, base64Image));
    }

    private IEnumerator PostRequest(string prompt, string base64Image)
    {
        var json = $"{{\"model\": \"llava\", \"prompt\": \"{prompt}\", \"images\": [\"{base64Image}\"]}}";
        var request = new UnityWebRequest(apiURL, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        request.uploadHandler = new UploadHandlerRaw(bodyRaw);
        request.downloadHandler = new DownloadHandlerBuffer();
        request.SetRequestHeader("Content-Type", "application/json");

        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError(request.error);
        }
        else
        {
            string response = request.downloadHandler.text;
            Debug.Log(response);
            UpdateResponseText(response);
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
