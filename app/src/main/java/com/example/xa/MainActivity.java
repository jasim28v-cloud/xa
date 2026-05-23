package com.example.xa;

import android.os.Bundle;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        WebView myWebView = findViewById(R.id.webview);
        WebSettings webSettings = myWebView.getSettings();
        webSettings.setJavaScriptEnabled(true); // مهم لتشغيل JavaScript
        myWebView.setWebViewClient(new WebViewClient());
        
        // تحميل ملف index.html الموجود في مجلد assets
        myWebView.loadUrl("file:///android_asset/index.html");
    }
}
