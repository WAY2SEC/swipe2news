package com.swipe2news.app;

import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Build;
import android.widget.RemoteViews;

import androidx.annotation.NonNull;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.work.Constraints;
import androidx.work.ExistingPeriodicWorkPolicy;
import androidx.work.ExistingWorkPolicy;
import androidx.work.NetworkType;
import androidx.work.OneTimeWorkRequest;
import androidx.work.PeriodicWorkRequest;
import androidx.work.WorkManager;
import androidx.work.Worker;
import androidx.work.WorkerParameters;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;
import java.util.TimeZone;
import java.util.concurrent.TimeUnit;

/**
 * Swipe2News live score card (owner, 27 Nov 2026): while a match is live, a pinned notification shows
 * "LIVE · FOOTBALL · swipe2news. — ⚽ ARS 1–0 CHE — 63' · Premier League" with our logo, also when the app is closed.
 * Data: https://swipe2news.com/editions/ng/football.json (refreshed every 10 min by the "Nigeria football" workflow).
 * Checks every 15 min; while a match is live it re-checks every 3 min. The card goes away at full time.
 * Only for readers who switched it on in the Football screen (LiveScoreToggleActivity).
 */
public class LiveScoreWorker extends Worker {
    static final String PREFS = "s2n_live", ON = "on", CHANNEL = "live_scores";
    static final int NOTE_ID = 4242;
    static final String FEED = "https://swipe2news.com/editions/ng/football.json";

    public LiveScoreWorker(@NonNull Context c, @NonNull WorkerParameters p) { super(c, p); }

    static boolean isOn(Context c) { return c.getSharedPreferences(PREFS, 0).getBoolean(ON, false); }

    static void setOn(Context c, boolean on) {
        c.getSharedPreferences(PREFS, 0).edit().putBoolean(ON, on).apply();
        WorkManager wm = WorkManager.getInstance(c);
        if (on) {
            Constraints net = new Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build();
            wm.enqueueUniquePeriodicWork("s2n-live-periodic", ExistingPeriodicWorkPolicy.UPDATE,
                    new PeriodicWorkRequest.Builder(LiveScoreWorker.class, 15, TimeUnit.MINUTES).setConstraints(net).build());
            wm.enqueueUniqueWork("s2n-live-now", ExistingWorkPolicy.REPLACE,
                    new OneTimeWorkRequest.Builder(LiveScoreWorker.class).setConstraints(net).build());
        } else {
            wm.cancelUniqueWork("s2n-live-periodic");
            wm.cancelUniqueWork("s2n-live-now");
            NotificationManagerCompat.from(c).cancel(NOTE_ID);
        }
    }

    @NonNull @Override
    public Result doWork() {
        Context c = getApplicationContext();
        if (!isOn(c)) return Result.success();
        try {
            JSONObject live = pick(fetch());
            if (live == null) { NotificationManagerCompat.from(c).cancel(NOTE_ID); return Result.success(); }
            show(c, live);
            // keep it fresh while the match is on
            WorkManager.getInstance(c).enqueueUniqueWork("s2n-live-now", ExistingWorkPolicy.REPLACE,
                    new OneTimeWorkRequest.Builder(LiveScoreWorker.class).setInitialDelay(3, TimeUnit.MINUTES)
                            .setConstraints(new Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()).build());
            return Result.success();
        } catch (Exception e) {
            return Result.retry();
        }
    }

    private static JSONObject fetch() throws Exception {
        HttpURLConnection h = (HttpURLConnection) new URL(FEED + "?t=" + System.currentTimeMillis() / 60000).openConnection();
        h.setConnectTimeout(15000); h.setReadTimeout(15000);
        h.setRequestProperty("Cache-Control", "no-cache");
        StringBuilder sb = new StringBuilder();
        try (BufferedReader r = new BufferedReader(new InputStreamReader(h.getInputStream(), "UTF-8"))) {
            String l; while ((l = r.readLine()) != null) sb.append(l);
        } finally { h.disconnect(); }
        return new JSONObject(sb.toString());
    }

    /** The most important live match: Super Eagles first, then the lowest priority number. */
    private static JSONObject pick(JSONObject d) {
        JSONArray ms = d.optJSONArray("matches");
        if (ms == null) return null;
        JSONObject best = null; int liveCount = 0;
        for (int i = 0; i < ms.length(); i++) {
            JSONObject m = ms.optJSONObject(i);
            if (m == null || !"in".equals(m.optString("state"))) continue;
            liveCount++;
            if (best == null || m.optInt("p", 9) < best.optInt("p", 9)) best = m;
        }
        if (best != null) try { best.put("_more", liveCount - 1); } catch (Exception ignored) {}
        return best;
    }

    private static String minute(JSONObject m) {
        if (m.optString("detail").toLowerCase(Locale.ROOT).contains("paus")) return "Half time";
        try {
            SimpleDateFormat f = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.ROOT);
            f.setTimeZone(TimeZone.getTimeZone("UTC"));
            Date t = f.parse(m.optString("t"));
            long e = (System.currentTimeMillis() - t.getTime()) / 60000;
            if (e <= 0) return "Kick-off";
            if (e <= 47) return e + "'";
            if (e < 63) return "Half time";
            return Math.min(90, e - 15) + "'";
        } catch (Exception ex) { return "Live"; }
    }

    private static void show(Context c, JSONObject m) {
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (Build.VERSION.SDK_INT >= 26 && nm.getNotificationChannel(CHANNEL) == null) {
            NotificationChannel ch = new NotificationChannel(CHANNEL, "Live football scores", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("A pinned score card while a match is on");
            ch.setSound(null, null); ch.enableVibration(false); ch.setShowBadge(false);
            nm.createNotificationChannel(ch);
        }
        boolean ng = "ng".equals(m.optString("ng"));
        String score = (ng ? "NG  " : "⚽  ") + m.optString("hs", m.optString("h")) + " " + num(m, "hg") + "–" + num(m, "ag") + " " + m.optString("as", m.optString("a"));
        int more = m.optInt("_more", 0);
        String sub = minute(m) + " · " + m.optString("lg") + (more > 0 ? " · +" + more + " more live" : "");

        RemoteViews v = new RemoteViews(c.getPackageName(), R.layout.live_score);
        v.setTextViewText(R.id.ls_score, score);
        v.setTextViewText(R.id.ls_sub, sub);

        Intent open = new Intent(Intent.ACTION_VIEW, Uri.parse("https://swipe2news.com/ng/?fb=1&source=android"));
        open.setPackage(c.getPackageName());
        open.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        PendingIntent pi = PendingIntent.getActivity(c, 1, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);

        NotificationCompat.Builder b = new NotificationCompat.Builder(c, CHANNEL)
                .setSmallIcon(R.drawable.ic_notification)
                .setContentTitle(score).setContentText(sub)          // for watches / accessibility / lock screen text
                .setCustomContentView(v).setCustomBigContentView(v)
                .setStyle(new NotificationCompat.DecoratedCustomViewStyle())
                .setColor(0xFF4A0E3F).setColorized(true)
                .setOngoing(true).setOnlyAlertOnce(true).setSilent(true)
                .setCategory(NotificationCompat.CATEGORY_STATUS)
                .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
                .setContentIntent(pi)
                .setTimeoutAfter(20 * 60 * 1000L);                    // vanishes if the app stops getting updates
        try { NotificationManagerCompat.from(c).notify(NOTE_ID, b.build()); } catch (SecurityException ignored) {}
    }

    private static String num(JSONObject m, String k) { return m.isNull(k) ? "0" : String.valueOf(m.optInt(k, 0)); }
}
