package ru.epaction.presentation

sealed class TypeTask {
    data object ClickBtn : TypeTask()
    data class AskTask(
        val question: String,
        val answer: String = "",
        val isEnable: Boolean = false
    ) : TypeTask()

    data class VoiceTask(val task: String): TypeTask()
    data class  VideoTask(val task: String): TypeTask()
}
