package com.google.firebase.quickstart.fcm.kotlin

import android.content.Context
import android.util.Log
import androidx.work.Worker
import androidx.work.WorkerParameters

class MyWorker(appContext: Context, workerParams: WorkerParameters) : Worker(appContext, workerParams) {

    override fun doWork(): Result {
        return Result.success()
    }

    companion object {
        private val TAG = "MyWorker"
    }
}
