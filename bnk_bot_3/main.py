  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_updater.py", line 384, in polling_action_cb
    raise exc
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_updater.py", line 373, in polling_action_cb
    updates = await self.bot.get_updates(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 618, in get_updates
    updates = await super().get_updates(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 542, in decorator
    result = await func(self, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 4164, in get_updates
    await self._post(
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 630, in _post
    return await self._do_post(
           ^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 347, in _do_post
    return await super()._do_post(
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 658, in _do_post
    return await request.post(
           ^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/request/_baserequest.py", line 200, in post
    result = await self._request_wrapper(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/request/_baserequest.py", line 381, in _request_wrapper
    raise Conflict(message)
telegram.error.Conflict: Conflict: terminated by other getUpdates request; make sure that only one bot instance is running
Traceback (most recent call last):
  File "/app/main.py", line 268, in <module>
    main()
  File "/app/main.py", line 252, in main
    load_stats_from_excel()
  File "/app/main.py", line 53, in load_stats_from_excel
    user_stats[user]['Флекса'] += flexa or 0
TypeError: unsupported operand type(s) for +=: 'float' and 'str'
Traceback (most recent call last):
  File "/app/main.py", line 268, in <module>
    main()
  File "/app/main.py", line 252, in main
    load_stats_from_excel()
  File "/app/main.py", line 53, in load_stats_from_excel
    user_stats[user]['Флекса'] += flexa or 0
TypeError: unsupported operand type(s) for +=: 'float' and 'str'
Traceback (most recent call last):
  File "/app/main.py", line 268, in <module>
    main()
  File "/app/main.py", line 252, in main
    load_stats_from_excel()
  File "/app/main.py", line 53, in load_stats_from_excel
    user_stats[user]['Флекса'] += flexa or 0
TypeError: unsupported operand type(s) for +=: 'float' and 'str'
Traceback (most recent call last):
  File "/app/main.py", line 268, in <module>
    main()
  File "/app/main.py", line 252, in main
    load_stats_from_excel()
  File "/app/main.py", line 53, in load_stats_from_excel
    user_stats[user]['Флекса'] += flexa or 0
TypeError: unsupported operand type(s) for +=: 'float' and 'str'
Traceback (most recent call last):
  File "/app/main.py", line 182, in <module>
    main()
  File "/app/main.py", line 169, in main
    load_stats_from_excel()
  File "/app/main.py", line 53, in load_stats_from_excel
    user_days[username].add(date.date())
                            ^^^^^^^^^
AttributeError: 'str' object has no attribute 'date'
Traceback (most recent call last):
  File "/app/main.py", line 182, in <module>
    main()
  File "/app/main.py", line 169, in main
    load_stats_from_excel()
  File "/app/main.py", line 53, in load_stats_from_excel
    user_days[username].add(date.date())
                            ^^^^^^^^^
AttributeError: 'str' object has no attribute 'date'
