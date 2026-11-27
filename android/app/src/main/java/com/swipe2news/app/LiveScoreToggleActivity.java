package com.swipe2news.app;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.widget.Toast;

/**
 * Opened from the Football screen of the Nigeria app:
 *   swipe2news://livescore?on=1  -> pin live scores (asks for notification permission on Android 13+)
 *   swipe2news://livescore?on=0  -> stop
 * No screen of its own: it saves the choice, shows a short message and closes.
 */
public class LiveScoreToggleActivity extends Activity {
    private static final int REQ = 77;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        Uri u = getIntent().getData();
        boolean on = u == null || !"0".equals(u.getQueryParameter("on"));
        if (!on) { LiveScoreWorker.setOn(this, false); done("Live scores off"); return; }
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ);
            return;
        }
        LiveScoreWorker.setOn(this, true);
        done("⚽ Live scores pinned – they show while a match is on");
    }

    @Override public void onRequestPermissionsResult(int code, String[] p, int[] r) {
        boolean ok = r.length > 0 && r[0] == PackageManager.PERMISSION_GRANTED;
        if (ok) LiveScoreWorker.setOn(this, true);
        done(ok ? "⚽ Live scores pinned – they show while a match is on" : "Allow notifications for Swipe2News to see live scores");
    }

    private void done(String msg) { Toast.makeText(this, msg, Toast.LENGTH_LONG).show(); finish(); }
}
