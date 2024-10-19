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

        // Add user's input in canvas output
        responseText.text += $"<b><color=#66ff66>User</color></b>\n";
        responseText.text += $"<color=#000000>{playerMessage}</color>\n";

        Debug.Log("Send player speech to AI agent");
        brainController.AddToAuditoryLanguageBuffer(playerMessage);
        sendButton.interactable = true;
    }
}
