package ru.epaction.di

import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.Response
import okhttp3.internal.platform.android.AndroidLogHandler.setLevel
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import ru.epaction.network.EPActionService

object ServiceLocator {
    fun getRetrofitService(): Retrofit {

        val logging = HttpLoggingInterceptor()
        logging.setLevel(HttpLoggingInterceptor.Level.BASIC)

        val client = OkHttpClient.Builder()
            .addInterceptor(Interceptor { chain ->
                val newRequest = chain.request().newBuilder()
                    .addHeader("DEVICE_ID", "21afb99f-197d-40cb-bef0-b479f9eb974d")
                    .build()
                chain.proceed(newRequest)
            })
            .addInterceptor(logging)
            .build()


        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .client(client)
            .build()
    }

    fun getEPActionService() = getRetrofitService().create(EPActionService::class.java)
}

private const val BASE_URL = "http://satoru-hakaton.simbirsoft/"
