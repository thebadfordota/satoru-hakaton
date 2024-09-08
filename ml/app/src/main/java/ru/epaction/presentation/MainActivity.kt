package ru.epaction.presentation

import android.Manifest
import android.Manifest.permission.MANAGE_EXTERNAL_STORAGE
import android.Manifest.permission.READ_EXTERNAL_STORAGE
import android.Manifest.permission.RECORD_AUDIO
import android.Manifest.permission.WRITE_EXTERNAL_STORAGE
import android.content.Context
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.media.MediaRecorder
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.draw.paint
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import com.google.android.gms.tasks.OnCompleteListener
import com.google.firebase.Firebase
import com.google.firebase.FirebaseApp
import com.google.firebase.messaging.messaging
import kotlinx.coroutines.CoroutineExceptionHandler
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.asRequestBody
import ru.epaction.R
import ru.epaction.di.ServiceLocator
import ru.epaction.ui.theme.EPactionTheme
import ru.epaction.ui.theme.bezierSansBold
import ru.epaction.ui.theme.bezierSansRegular
import java.io.File

class MainActivity : ComponentActivity() {

    private val viewModel: MainViewModel by viewModels { MainViewModel.Factory }
    val isHorror = MutableStateFlow(true)

    val pickMedia = registerForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
        if (uri != null) {
            val file = getFileFromUri(uri)
            if (file == null) {
                Toast.makeText(this, "File not found", Toast.LENGTH_SHORT).show()
                return@registerForActivityResult
            }

            lifecycleScope.launch() {
                uploadFile(file)
            }
        }
    }

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission(),
    ) { isGranted: Boolean ->
        if (isGranted) {
            Toast.makeText(this, "Notifications permission granted", Toast.LENGTH_SHORT)
                .show()
        } else {
            Toast.makeText(
                this,
                "FCM can't post notifications without POST_NOTIFICATIONS permission",
                Toast.LENGTH_LONG,
            ).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val sharedPref = getPreferences(Context.MODE_PRIVATE)
        initFirebase(sharedPref)

        if (ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECORD_AUDIO
            ) != PackageManager.PERMISSION_GRANTED && ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.WRITE_EXTERNAL_STORAGE
            ) != PackageManager.PERMISSION_GRANTED && ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.READ_EXTERNAL_STORAGE
            ) != PackageManager.PERMISSION_GRANTED && ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.MANAGE_EXTERNAL_STORAGE
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            val permissions = arrayOf(
                android.Manifest.permission.RECORD_AUDIO,
                android.Manifest.permission.WRITE_EXTERNAL_STORAGE,
                android.Manifest.permission.READ_EXTERNAL_STORAGE,
                MANAGE_EXTERNAL_STORAGE
            )
            ActivityCompat.requestPermissions(this, permissions, 0)
        }

        if (!checkPermissions()) {
            requestPermissions()
        }

        setContent {
            EPactionTheme {
                // A surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier
                        .fillMaxSize(),
                ) {
                    val viewState by viewModel.state.collectAsState()
                    val checked by isHorror.collectAsState()


                    Screen(
                        viewState = viewState,
                        viewModel = viewModel,
                        onVoiceStart = ::startRecording,
                        onSelectVideo = {
                            pickMedia.launch(
                                PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.VideoOnly)
                            )
                        },
                        modifier = Modifier.fillMaxSize(),
                        isCheck = checked,
                        onChangChecked = { isHorror.update { it } }
                    )

                }
            }
        }

        askNotificationPermission()
    }

    private fun getFileFromUri(uri: Uri): File? {
        val filePathColumn = arrayOf(MediaStore.Images.Media.DATA)
        val cursor = contentResolver.query(uri, filePathColumn, null, null, null)
        cursor?.moveToFirst()
        val columnIndex = cursor?.getColumnIndex(filePathColumn[0])
        val filePath = cursor?.getString(columnIndex!!)
        cursor?.close()
        return filePath?.let { File(it) }
    }

    private fun initFirebase(sharedPref: SharedPreferences) {
        FirebaseApp.initializeApp(this)
        var token = sharedPref.getString(FIREBASE_TOKEN, null)
        if (token.isNullOrBlank()) {
            Firebase.messaging.token.addOnCompleteListener(
                OnCompleteListener { task ->
                    if (!task.isSuccessful) {
                        Log.w(TAG, "Fetching FCM registration token failed", task.exception)
                        return@OnCompleteListener
                    }

                    token = task.result
                    sharedPref.edit().apply {
                        putString(FIREBASE_TOKEN, token)
                        apply()
                    }

                },
            )
        }

        val msg = getString(R.string.msg_token_fmt, token)
        Log.d(TAG, msg)
    }

    private fun askNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) ==
                PackageManager.PERMISSION_GRANTED
            ) {
            } else {
                requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
    }

    private fun startRecording() {
        if (checkPermissions()) {
            val fileName = "${externalCacheDir?.absolutePath}/audiorecordtest.3gp"
            lifecycleScope.launch {
                val recorder = MediaRecorder().apply {
                    setAudioSource(MediaRecorder.AudioSource.MIC)
                    setOutputFormat(MediaRecorder.OutputFormat.AAC_ADTS)
                    setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                    setOutputFile(fileName)
                    prepare()
                    start()
                }
                delay(3000L)
                viewModel.startProgress()
                recorder.pause()
                recorder.release()

                uploadFile(file = File(fileName))
            }
        } else {
            requestPermissions()
        }
    }

    private suspend fun uploadFile(file: File) = withContext(Dispatchers.IO) {
        val code = ServiceLocator.getEPActionService().postAudio(
            MultipartBody.Part.createFormData(
                "file",
                file.name,
                file.asRequestBody("multipart/form-data".toMediaTypeOrNull())
            )
        )
        withContext(Dispatchers.Main){
            viewModel.startProgress()
        }
    }

    fun checkPermissions(): Boolean {
        // this method is used to check permission
        val result = ContextCompat.checkSelfPermission(applicationContext, WRITE_EXTERNAL_STORAGE)
        val result1 = ContextCompat.checkSelfPermission(applicationContext, RECORD_AUDIO)
        return result == PackageManager.PERMISSION_GRANTED && result1 == PackageManager.PERMISSION_GRANTED
    }

    private fun requestPermissions() {
        // this method is used to request the
        // permission for audio recording and storage.
        ActivityCompat.requestPermissions(
            this@MainActivity,
            arrayOf<String>(
                RECORD_AUDIO,
                WRITE_EXTERNAL_STORAGE,
                READ_EXTERNAL_STORAGE,
                MANAGE_EXTERNAL_STORAGE
            ),
            0
        )
    }

    companion object {
        private const val TAG = "MainActivity"
        private const val FIREBASE_TOKEN = "firebase_token"
    }
}

@Composable
fun Screen(
    viewState: ViewState,
    viewModel: MainViewModel,
    onVoiceStart: () -> Unit,
    onSelectVideo: () -> Unit,
    isCheck: Boolean,
    onChangChecked: (Boolean) -> Unit,
    modifier: Modifier
) {
    when (viewState) {
        is ViewState.Start -> StartScreen(isCheck)
        is ViewState.Connect -> ConnectServiceScreen(
            viewState.code,
            viewModel::onCodeChanged,
            isProgress = viewState.isProgress,
            isEnabledBtn = viewState.isEnabled,
            onConnect = viewModel::onConnectClick,
            isHideKeyboard = viewState.isHideKeyboard,
            isCheck = isCheck
        )

        is ViewState.Success -> SuccessScreen(
            isCheck = isCheck,
            onChangChecked = onChangChecked,
            code = viewState.code,
            modifier = modifier,
            isHorror = isCheck
        )

        is ViewState.Task -> TaskScreen(
            viewModel,
            viewState.type,
            viewState.isProgress,
            viewState.isError,
            onVoiceStart,
            onSelectVideo,
            isCheck,
            onChangChecked,
            modifier = modifier
        )
    }
}

@Composable
fun StartScreen(isCheck: Boolean, modifier: Modifier = Modifier) {
    Box(
        modifier
            .fillMaxSize()
            .setBackground(isCheck)
    ) {
        Image(
            modifier = modifier
                .size(109.dp, 106.dp)
                .align(Alignment.Center),
            painter = painterResource(id = R.drawable.app_icon),
            contentDescription = null
        )
    }
}

@Composable
fun TaskScreen(
    viewModel: MainViewModel,
    type: TypeTask,
    isProgress: Boolean,
    isError: Boolean,
    onVoiceStart: () -> Unit,
    onSelectVideo: () -> Unit,
    isCheck: Boolean,
    onChangChecked: (Boolean) -> Unit,
    modifier: Modifier = Modifier
) {
    when {
        isProgress -> Loader(isCheck, modifier)
        isError -> Error(isCheck, modifier)
        type is TypeTask.ClickBtn -> ClickBtnScreen(isCheck, viewModel::onPeachClick)
        type is TypeTask.AskTask -> AskScreen(
            question = type.question,
            answer = type.answer,
            onAnswerChange = viewModel::onAnswerChange,
            onSendAnswer = viewModel::onSendAnswer,
            isEnabledBtn = type.isEnable,
            isHorror = isCheck
        )

        type is TypeTask.VoiceTask -> VoiceScreen(
            isHorror = isCheck,
            task = type.task,
            onVoiceStart = onVoiceStart
        )

        type is TypeTask.VideoTask -> VideoScreen(
            isHorror = isCheck,
            task = type.task,
            onSelectClick = onSelectVideo
        )
    }
}

@Composable
fun Error(isCheck: Boolean, modifier: Modifier = Modifier) {
    Box(
        modifier
            .fillMaxSize()
            .setBackground(isCheck)
    ) {
        Icon(
            modifier = Modifier
                .size(171.dp)
                .align(Alignment.Center),
            painter = painterResource(id = R.drawable.baseline_close_24),
            tint = Color.Red,
            contentDescription = null
        )
    }
}

@Composable
fun ClickBtnScreen(isCheck: Boolean, onClick: (Int) -> Unit, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .setBackground(isCheck)
    ) {
        Column(
            modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceAround
        ) {
            repeat(3) {
                Image(
                    modifier = modifier
                        .size(171.dp)
                        .clickable { onClick(it) },
                    painter = painterResource(id = R.drawable.peach),
                    contentDescription = null
                )
            }
        }

    }
}

@Composable
fun ConnectServiceScreen(
    code: String,
    onCodeChanged: (String) -> Unit,
    isProgress: Boolean,
    isEnabledBtn: Boolean,
    isHideKeyboard: Boolean,
    onConnect: () -> Unit,
    isCheck: Boolean,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .setBackground(isCheck)
    ) {
        if (isProgress) {
            Loader(isCheck, modifier)
        } else {
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center,
                modifier = modifier.align(Alignment.BottomCenter)
            ) {

                Column(modifier = modifier.weight(1f)) {
                    Spacer(modifier = modifier.height(195.dp))
                    Text(
                        modifier = modifier,
                        text = stringResource(id = R.string.app_name),
                        fontSize = 50.sp,
                        fontFamily = bezierSansBold
                    )
                }

                Column(
                    modifier = modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .background(Color.White, RoundedCornerShape(50.dp, 50.dp, 0.dp, 0.dp)),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Spacer(modifier = modifier.height(54.dp))
                    Text(
                        modifier = modifier,
                        text = stringResource(id = R.string.code_title),
                        fontSize = 35.sp,
                        fontFamily = bezierSansRegular
                    )
                    Spacer(modifier = modifier.height(46.dp))
                    OutlinedTextField(
                        value = code,
                        onValueChange = onCodeChanged,
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        shape = RoundedCornerShape(33.dp),
                        modifier = modifier
                    )

                    Spacer(modifier = Modifier.height(36.dp))

                    val focusManager = LocalFocusManager.current

                    if (isHideKeyboard) {
                        focusManager.clearFocus()
                    }

                    ActionButton(
                        text = stringResource(id = R.string.connect),
                        onClick = onConnect,
                        isEnabledBtn = isEnabledBtn
                    )
                }
            }
        }
    }
}

@Composable
fun ActionButton(
    text: String,
    onClick: () -> Unit,
    isEnabledBtn: Boolean,
    modifier: Modifier = Modifier,
) {
    OutlinedButton(
        onClick = onClick,
        enabled = isEnabledBtn,
        modifier = modifier,
        border = null,
        colors = ButtonDefaults.outlinedButtonColors(contentColor = Color.Black)
    ) {
        Text(text, fontSize = 25.sp)
    }
}

@Composable
fun Loader(isCheck: Boolean, modifier: Modifier = Modifier) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .setBackground(isCheck), contentAlignment = Alignment.Center
    ) {
        CircularProgressIndicator(
            color = MaterialTheme.colorScheme.secondary,
            trackColor = MaterialTheme.colorScheme.surfaceVariant,
        )
    }
}

@Composable
fun SuccessScreen(
    isCheck: Boolean,
    onChangChecked: (Boolean) -> Unit,
    code: String,
    isHorror: Boolean,
    modifier: Modifier
) {
    Box(modifier.setBackground(isHorror), contentAlignment = Alignment.Center) {
        Text(text = code, fontSize = 48.sp)
    }
}

@Composable
fun MainScreen(
    onSubscribeClick: () -> Unit,
    onLogTokenClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column {
        Image(
            painter = painterResource(R.drawable.ic_launcher_foreground),
            contentDescription = null,
            modifier = Modifier
                .fillMaxWidth()
                .align(Alignment.CenterHorizontally)
                .padding(16.dp)
        )

        Text(
            text = stringResource(id = R.string.quickstart_message),
            style = MaterialTheme.typography.bodyMedium,
            color = Color.Black,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier
                .align(Alignment.CenterHorizontally)
                .padding(16.dp),
        )

        Button(
            onClick = onSubscribeClick,
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
                .align(Alignment.CenterHorizontally)
        ) {
            Text(text = "Подписаться на погоду")
        }

        Button(
            onClick = onLogTokenClick,
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
                .align(Alignment.CenterHorizontally),
        ) {
            Text("Войти с помощью токена")
        }

    }
}

@Composable
fun AskScreen(
    question: String,
    answer: String,
    onAnswerChange: (String) -> Unit,
    onSendAnswer: () -> Unit,
    isEnabledBtn: Boolean,
    isHorror: Boolean,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .setBackground(isHorror)
    ) {
        Column(
            modifier
                .align(Alignment.Center)
                .padding(16.dp)
        ) {

            Text(
                text = question,
                modifier
                    .fillMaxWidth()
                    .background(Color.White, RoundedCornerShape(36.dp))
                    .padding(16.dp),
                fontSize = 24.sp
            )

            Spacer(modifier = modifier.height(40.dp))

            val focusManager = LocalFocusManager.current
            OutlinedTextField(
                modifier = modifier
                    .fillMaxWidth()
                    .background(Color.White, CircleShape),
                value = answer,
                onValueChange = onAnswerChange,
                shape = RoundedCornerShape(33.dp),
                keyboardActions = KeyboardActions(onDone = { focusManager.clearFocus() }),
                keyboardOptions = KeyboardOptions.Default.copy(imeAction = ImeAction.Done),
                textStyle = TextStyle(fontSize = 24.sp)
            )

            Spacer(modifier = modifier.height(40.dp))

            ActionButton(
                text = stringResource(id = R.string.answer_btn),
                onClick = onSendAnswer,
                isEnabledBtn = isEnabledBtn,
                modifier = modifier.fillMaxWidth()
            )
        }
    }
}

@Composable
fun VoiceScreen(
    isHorror: Boolean,
    task: String,
    onVoiceStart: () -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .setBackground(isHorror)
            .padding(top = 80.dp, bottom = 40.dp, start = 40.dp, end = 40.dp)
    ) {
        Image(
            painter = painterResource(id = R.drawable.man_singer),
            contentDescription = null,
            modifier
                .fillMaxWidth()
                .size(200.dp)
        )

        Text(
            text = task,
            modifier
                .fillMaxWidth()
                .background(Color.White, RoundedCornerShape(36.dp))
                .padding(16.dp)
                .align(Alignment.Center),
            fontSize = 24.sp,
            textAlign = TextAlign.Center
        )

        IconButton(
            modifier = modifier
                .size(48.dp)
                .align(Alignment.BottomCenter), onClick = onVoiceStart
        ) {
            Icon(
                painter = painterResource(id = R.drawable.microphone),
                contentDescription = null,
                tint = Color(0xFF8597A8)
            )
        }
    }
}

@Composable
fun VideoScreen(
    isHorror: Boolean,
    task: String,
    onSelectClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .setBackground(isHorror)
            .padding(top = 80.dp, bottom = 40.dp, start = 40.dp, end = 40.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = task,
            modifier
                .fillMaxWidth()
                .background(Color.White, RoundedCornerShape(36.dp))
                .padding(16.dp),
            fontSize = 24.sp,
            textAlign = TextAlign.Center
        )

        Spacer(modifier = modifier.size(40.dp))

        OutlinedButton(
            onClick = onSelectClick,
            modifier = modifier,
            border = null,
            colors = ButtonDefaults.outlinedButtonColors(contentColor = Color.Black)
        ) {
            Text("Выбрать", fontSize = 25.sp)
        }

    }
}

@Preview(showBackground = true, widthDp = 360, heightDp = 780)
@Composable
fun GreetingPreview() {
    EPactionTheme {

    }
}

fun Modifier.setBackground(isHorror: Boolean = true): Modifier =
    composed {
        this.paint(
            painter = painterResource(id = R.drawable.background),
            contentScale = ContentScale.FillBounds
        )
    }

