using System;
using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using UnityEngine.UI;
using TMPro;
using CandyCoded.env;
using AIden;

public class PlayerChatUIController : MonoBehaviour
{
    public TMP_InputField playerInputField;
    public TMP_Text responseText;
    public Button sendButton;
    public PlayerChatMenuToggle playerChatMenuToggle;
    public TMP_Text logOutput;


    private void Start()
    {
        sendButton.onClick.AddListener(SendMessageToAIden);
    }

    private void SendMessageToAIden()
    {
        // Get AI agent's brain controller
        GameObject aiAgent = playerChatMenuToggle.GetCurrentAIAgent();
        BrainController brainController = aiAgent.GetComponentInChildren<BrainController>();

        string playerMessage = playerInputField.text;
        sendButton.interactable = false;

        // Add user's input in canvas and log outputs
        string playerMessageFormatted = $"<b><color=#66ff66>User</color></b>\n";
        playerMessageFormatted += $"{playerMessage}\n";
        responseText.text += playerMessageFormatted;
        if (logOutput != null) logOutput.text += playerMessageFormatted;

        Debug.Log("Send player speech to AI agent: " + playerMessage);
        brainController.AddToAuditoryLanguageBuffer(playerMessage);

        playerInputField.text = "";
        sendButton.interactable = true;
    }
}
