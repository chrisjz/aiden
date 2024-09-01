using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using CandyCoded.env;

public class VisionAPIUIController : MonoBehaviour
{
    public Camera cameraToCapture;
    public TMP_Text responseText;
    public Button sendButton;
    public bool saveInput = false;

    private VisionAPIClient visionApiClient;

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
            string apiUrl = $"{protocol}://{host}:{port}/occipital";
            visionApiClient = new VisionAPIClient(apiUrl);
            Debug.Log($"Brain API URL set to: {apiUrl}");
        }
        else
        {
            Debug.LogError("Missing environment variables for brain API URL.");
            return;
        }

        sendButton.onClick.AddListener(OnSendButtonClicked);
    }

    private void OnSendButtonClicked()
    {
        sendButton.interactable = false;

        Texture2D capturedImage = visionApiClient.CaptureCameraRenderTexture(cameraToCapture);
        string base64Image = visionApiClient.TextureToBase64(capturedImage);

        // Save the captured image to a file
        visionApiClient.SaveImageToFile(capturedImage, saveInput);

        Debug.Log("Start vision inference.");
        StartCoroutine(visionApiClient.SendRequestToVisionAPI(base64Image, UpdateResponseText));
    }

    private void UpdateResponseText(string text)
    {
        responseText.text = text;
        sendButton.interactable = true;
    }
}
