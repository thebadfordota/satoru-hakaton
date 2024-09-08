package ru.epaction.presentation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import ru.epaction.di.ServiceLocator
import ru.epaction.network.EPActionService
import ru.epaction.network.ResultRequest
import ru.epaction.network.TaskResponse

class MainViewModel(val epActionService: EPActionService) : ViewModel() {
    val state: MutableStateFlow<ViewState> = MutableStateFlow(ViewState.Start)

    init {
        viewModelScope.launch {
            val task = epActionService.getTask().body()
            delay(1000)
            state.update {
                when (task?.task_type) {
                    "peach" -> ViewState.Task(type = TypeTask.ClickBtn)
                    "voice" -> ViewState.Task(type = TypeTask.VoiceTask(task.task_content.orEmpty()))
                    else -> ViewState.Task(type = TypeTask.VideoTask(task?.task_content.orEmpty()))
                }
            }
        }
    }

    fun onCodeChanged(input: String) {
        if (input.length < MAX_LENGTH_CODE) {
            state.update {
                (it as ViewState.Connect).copy(
                    code = input,
                    isEnabled = false,
                    isHideKeyboard = false
                )
            }
        } else if (input.length == MAX_LENGTH_CODE) {
            state.update {
                (it as ViewState.Connect).copy(
                    code = input,
                    isEnabled = true,
                    isHideKeyboard = true
                )
            }
        }
    }

    fun onConnectClick() {
        state.update { (it as ViewState.Connect).copy(isProgress = true) }

        state.update { ViewState.Task(type = TypeTask.ClickBtn) }
        /*viewModelScope.launch {
            activateCode()
            delay(60000)
        }*/

        //TODO запрос
    }

    fun onPeachClick(item: Int) = viewModelScope.launch {
        if (item == (0..2).random()) {
            state.update { (it as ViewState.Task).copy(isProgress = true) }
            epActionService.result(ResultRequest(true))
            delay(500L)
            activateCode()
        } else {
            state.update { (it as ViewState.Task).copy(isError = true, isProgress = false) }
            delay(500L)
            state.update { (it as ViewState.Task).copy(isError = false) }
        }
    }

    fun activateCode() {
        viewModelScope.launch {
            delay(100L)
            state.update { ViewState.Success(code = generateCode()) }
            activateCode()
        }
    }

    private fun generateCode(): String = (0..9).shuffled().take(6).joinToString("")

    fun onAnswerChange(answer: String) {
        state.update {
            (it as ViewState.Task).copy(
                type = (it.type as TypeTask.AskTask).copy(
                    answer = answer,
                    isEnable = answer.isNotEmpty()
                )
            )
        }
    }

    fun onSendAnswer() = viewModelScope.launch {
        state.update {
            (it as ViewState.Task).copy(
                isProgress = true
            )
        }
        delay(1000L)
        state.update {
            (it as ViewState.Task).copy(
                isProgress = false
            )
        }
    }

    fun onStartRecord() {
        TODO("Not yet implemented")
    }

    fun startProgress() = viewModelScope.launch {
        state.update { (it as ViewState.Task).copy(isProgress = true) }
        delay(500L)
        activateCode()
    }

    companion object {
        private const val MAX_LENGTH_CODE = 6

        val Factory: ViewModelProvider.Factory = viewModelFactory {
            initializer {
                MainViewModel(ServiceLocator.getEPActionService())
            }
        }
    }
}
