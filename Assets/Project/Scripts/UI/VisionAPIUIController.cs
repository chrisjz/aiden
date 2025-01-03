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
        visionApiClient = new VisionAPIClient(cameraToCapture, saveInput);

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

        Debug.Log("Start vision inference.");
        StartCoroutine(visionApiClient.GetVisionDataCoroutine(
                occipitalData => UpdateResponseText(occipitalData),
                error => Debug.LogError(error)
            ));
    }

    private void UpdateResponseText(string text)
    {
        string responseTitle = $"<b><color=#6666FF>Agent's captured visual</color></b>";  // Bold and blue
        if (responseText != null) responseText.text += responseTitle + text + "\n";
        sendButton.interactable = true;
    }
}
