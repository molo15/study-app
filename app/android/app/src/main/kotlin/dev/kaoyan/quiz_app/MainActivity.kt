package dev.kaoyan.quiz_app

import android.content.ContentValues
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import java.io.File
import java.io.FileOutputStream

class MainActivity : FlutterActivity() {
    private val channel = "dev.kaoyan.quiz_app/exporter"

    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, channel)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "saveToDownloads" -> {
                        val fileName = call.argument<String>("fileName") ?: "export.json"
                        val content: ByteArray = when (val c = call.argument<Any>("content")) {
                            is String -> c.toByteArray(Charsets.UTF_8)
                            is ByteArray -> c
                            else -> ByteArray(0)
                        }
                        try {
                            result.success(saveToDownloads(fileName, content))
                        } catch (e: Exception) {
                            result.error("SAVE_FAILED", e.message, null)
                        }
                    }
                    else -> result.notImplemented()
                }
            }
    }

    /** 把内容写入系统公共「下载」目录（文件管理/下载中可见），返回展示路径。 */
    private fun saveToDownloads(fileName: String, content: ByteArray): String {
        // Android 10+ (API 29+) 用 MediaStore 写公共 Downloads，无需存储权限
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val resolver = contentResolver
            val values = ContentValues().apply {
                put(MediaStore.Downloads.DISPLAY_NAME, fileName)
                put(MediaStore.Downloads.MIME_TYPE, "application/json")
                put(MediaStore.Downloads.IS_PENDING, 1)
            }
            var uri: Uri? = null
            try {
                uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
                resolver.openOutputStream(uri!!).use { it?.write(content) }
                values.clear()
                values.put(MediaStore.Downloads.IS_PENDING, 0)
                resolver.update(uri!!, values, null, null)
                val target = android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI
                val outName = android.os.Environment.DIRECTORY_DOWNLOADS +
                    File.separator + fileName
                return outName
            } catch (e: Exception) {
                uri?.let { resolver.delete(it, null, null) }
                throw e
            }
        } else {
            // 旧版 Android：写入外部存储的公共下载目录（需 WRITE_EXTERNAL_STORAGE 权限）
            val dir = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_DOWNLOADS
            )
            if (!dir.exists()) dir.mkdirs()
            val file = File(dir, fileName)
            FileOutputStream(file).use { it.write(content) }
            return file.absolutePath
        }
    }
}
