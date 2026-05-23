# قواعد أساسية للتطبيق
-keepattributes Signature
-keepattributes *Annotation*

# الحفاظ على الدوال الأصلية
-keepclasseswithmembernames class * {
    native <methods>;
}

# الحفاظ على Custom Views
-keep public class * extends android.view.View {
    public <init>(android.content.Context);
    public <init>(android.content.Context, android.util.AttributeSet);
    public <init>(android.content.Context, android.util.AttributeSet, int);
}
