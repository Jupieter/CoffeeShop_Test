'''
Module of Android API for plyer.notification.

.. versionadded:: 1.0.0

.. versionchanged:: 1.4.0
    Fixed notifications not displaying due to missing NotificationChannel
    required by Android Oreo 8.0+ (API 26+).

.. versionchanged:: 1.4.0
    Added simple toaster notification.

.. versionchanged:: 1.4.0
    Fixed notifications not displaying big icons properly.
    Added option for custom big icon via `icon`.
'''

from android import python_act
from android.runnable import run_on_ui_thread
from jnius import autoclass, cast

from plyer.facades import Notification
from plyer.platforms.android import activity, SDK_INT

AndroidString = autoclass('java.lang.String')
Context = autoclass('android.content.Context')
NotificationBuilder = autoclass('android.app.Notification$Builder')
NotificationManager = autoclass('android.app.NotificationManager')
PendingIntent = autoclass('android.app.PendingIntent')
Intent = autoclass('android.content.Intent')
Toast = autoclass('android.widget.Toast')
BitmapFactory = autoclass('android.graphics.BitmapFactory')


class AndroidNotification(Notification):
    '''
    Implementation of Android notification API.

    .. versionadded:: 1.0.0
    '''

    def __init__(self):
        print("notification __init__")
        package_name = activity.getPackageName()
        print("activity:  ", activity)
        print("package_name:  ",package_name)
        self._ns = None
        self._channel_id = package_name

        pm = activity.getPackageManager()
        info = pm.getApplicationInfo(package_name, 0)
        print("info first", info)
        print("info.icon",info.icon)
        try:
            info = pm.getActivityInfo(activity.getComponentName(), 0)
            if info.icon == 0:
                # Take the application icon instead.
                info = pm.getApplicationInfo(package_name, 0) 
            self._app_icon = info.icon
            print("info.icon:  ",info.icon)
        except:
            self._app_icon = None

    def _get_notification_service(self):
        print("_get_notification_service")
        print("self._ns 1:  ",self._ns)
        if not self._ns:
            self._ns = cast(NotificationManager, activity.getSystemService(
                Context.NOTIFICATION_SERVICE
            ))
        print("self._ns 2:  ",self._ns)
        return self._ns

    def _build_notification_channel(self, name):
        '''
        Create a NotificationChannel using channel id of the application
        package name (com.xyz, org.xyz, ...) and channel name same as the
        provided notification title if the API is high enough, otherwise
        do nothing.

        .. versionadded:: 1.4.0
        '''

        if SDK_INT < 26:
            return

        channel = autoclass('android.app.NotificationChannel')

        app_channel = channel(
            self._channel_id, name, NotificationManager.IMPORTANCE_DEFAULT
        )
        self._get_notification_service().createNotificationChannel(
            app_channel
        )
        return app_channel

    @run_on_ui_thread
    def _toast(self, message):
        '''
        Display a popup-like small notification at the bottom of the screen.

        .. versionadded:: 1.4.0
        '''
        print("notification toast")
        Toast.makeText(
            activity,
            cast('java.lang.CharSequence', AndroidString(message)),
            Toast.LENGTH_LONG
        ).show()

    def _set_icons(self, notification, icon=None):
        '''
        Set the small application icon displayed at the top panel together with
        WiFi, battery percentage and time and the big optional icon (preferably
        PNG format with transparent parts) displayed directly in the
        notification body.

        .. versionadded:: 1.4.0
        '''
        print("icon: ", icon)
        app_icon = self._app_icon  # BitmapFactory.decodeFile('image/Coffee_icon_24.png')
        print("app_icon: ", app_icon)

        bitmap_icon = None # app_icon
        if icon is not None:
            bitmap_icon = BitmapFactory.decodeFile(icon)
            notification.setLargeIcon(bitmap_icon)
        elif icon == '':
            # we don't want the big icon set,
            # only the small one in the top panel
            pass
        else:
            print("decodeResource")
            bitmap_icon = BitmapFactory.decodeResource(
                python_act.getResources(), app_icon
            )
            notification.setLargeIcon(bitmap_icon)
        print("bitmap_icon  ", bitmap_icon)
        notification.setSmallIcon(app_icon)

    def _build_notification(self, title):
        '''
        .. versionadded:: 1.4.0
        '''
        print("In the   _build_notification")
        if SDK_INT < 26:
            noti = NotificationBuilder(activity)
        else:
            self._channel = self._build_notification_channel(title)
            noti = NotificationBuilder(activity, self._channel_id)
        return noti

    @staticmethod
    def _set_open_behavior(notification):
        '''
        Open the source application when user opens the notification.

        .. versionadded:: 1.4.0
        '''

        # create Intent that navigates back to the application
        app_context = activity.getApplication().getApplicationContext()
        notification_intent = Intent(app_context, python_act)

        # set flags to run our application Activity
        notification_intent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)
        notification_intent.setAction(Intent.ACTION_MAIN)
        notification_intent.addCategory(Intent.CATEGORY_LAUNCHER)

        # get our application Activity
        pending_intent = PendingIntent.getActivity(
            app_context, 0, notification_intent, 0
        )

        notification.setContentIntent(pending_intent)
        notification.setAutoCancel(True)

    def _open_notification(self, notification):
        print("SDK_INT : ",SDK_INT)
        if SDK_INT >= 16:
            notification = notification.build()
            print("SDK_INT > 16")
        else:
            notification = notification.getNotification()
            print("SDK_INT < 16")
        print("notification: ",notification)
        self._get_notification_service().notify(0, notification)

    def _notify(self, **kwargs):
        print("In the _notify")
        noti = None
        message = kwargs.get('message').encode('utf-8')
        ticker = kwargs.get('ticker').encode('utf-8')
        title = AndroidString(
            kwargs.get('title', '').encode('utf-8')
        )
        icon = kwargs.get('app_icon')
        print("title",title, "message", message,"icon",icon, "toast",kwargs.get('toast'))

        # decide whether toast only or proper notification
        if kwargs.get('toast'):
            self._toast(message)
            return
        else:
            noti = self._build_notification(title)

        # set basic properties for notification
        print("noti 1:  ", noti)
        noti.setContentTitle(title)
        noti.setContentText(AndroidString(message))
        noti.setTicker(AndroidString(ticker))
        print("noti 2:  ", noti)
        # set additional flags for notification
        self._set_icons(noti, icon=icon)
        self._set_open_behavior(noti)
        print("noti 3:  ", noti)

        # launch
        self._open_notification(noti)


def instance():
    '''
    Instance for facade proxy.
    '''
    return AndroidNotification()

