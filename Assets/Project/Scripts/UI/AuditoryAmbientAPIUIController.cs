using System;
using UnityEngine;
using UnityEngine.UI;
using TMPro;

public class AuditoryAmbientAPIUIController : MonoBehaviour
{
    public TMP_Text responseText;
    public Button sendButton;
    public bool saveCapturedAudio = false;

    public AIAudioCapture audioCapture; // Reference to the AIAudioCapture script

    private AuditoryAPIClient auditoryApiClient;

    private void Start()
    {
        auditoryApiClient = new AuditoryAPIClient(audioCapture);

        if (!auditoryApiClient.IsAPIEnabled())
        {
            Debug.Log("Auditory Ambient API is disabled or not configured.");
            return;
        }

        sendButton.onClick.AddListener(OnSendButtonClicked);
    }

    private void OnSendButtonClicked()
    {
        sendButton.interactable = false;

        Debug.Log("Start auditory ambient inference.");
        StartCoroutine(auditoryApiClient.GetAuditoryDataCoroutine(
                auditoryData => UpdateResponseText(auditoryData),
                error => Debug.LogError(error)
            ));
    }

    private void UpdateResponseText(string text)
    {
        responseText.text = text;
        sendButton.interactable = true;
    }
}
