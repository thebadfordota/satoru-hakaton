package ru.epaction.network

import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface EPActionService {
    @Multipart
    @POST("/api/action/result/file")
    suspend fun postAudio(
        @Part file: MultipartBody.Part
    ): Response<Any>

    @GET("/api/action/task")
    suspend fun getTask(): Response<TaskResponse>

    @POST("/api/action/result/simple")
    suspend fun result(@Body request: ResultRequest): Response<Any>
}
