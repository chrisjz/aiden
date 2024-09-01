using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class VisionAPIUIController : MonoBehaviour
{
    public Camera cameraToCapture;
    public TMP_Text responseText;
    public Button sendButton;
    public bool saveInput = false;

    private VisionAPIClient visionApiClient;

    private void Start()
    {
        visionApiClient = new VisionAPIClient();

        if (!visionApiClient.IsAPIEnabled())
        {
            Debug.Log("Vision API is disabled or not configured.");
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
