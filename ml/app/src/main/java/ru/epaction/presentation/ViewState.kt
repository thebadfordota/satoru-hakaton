package ru.epaction.presentation

sealed class ViewState {
    data object Start : ViewState()

    data class Connect(
        val code: String = "",
        val isProgress: Boolean = false,
        val isEnabled: Boolean = false,
        val isHideKeyboard: Boolean = false
    ) : ViewState()

    data class Success(
        val code: String
    ) : ViewState()

    data class Task(
        val type: TypeTask,
        val isProgress: Boolean = false,
        val isError: Boolean = false,
    ) : ViewState()

    //data class
}


