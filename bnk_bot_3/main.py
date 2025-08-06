Traceback (most recent call last):
  File "/app/main.py", line 172, in <module>
    main()
  File "/app/main.py", line 157, in main
    app = ApplicationBuilder().token(TOKEN).job_queue().build()
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: ApplicationBuilder.job_queue() missing 1 required positional argument: 'job_queue'
Traceback (most recent call last):
  File "/app/main.py", line 172, in <module>
    main()
  File "/app/main.py", line 157, in main
    app = ApplicationBuilder().token(TOKEN).job_queue().build()
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: ApplicationBuilder.job_queue() missing 1 required positional argument: 'job_queue'
No error handlers are registered, logging exception.
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_application.py", line 1264, in process_update
    await coroutine
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_handlers/basehandler.py", line 157, in handle_update
    return await self.callback(update, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/main.py", line 84, in handle_message
    await update.message.reply_text(report.strip())
  File "/usr/local/lib/python3.11/site-packages/telegram/_message.py", line 1809, in reply_text
    return await self.get_bot().send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 2820, in send_message
    return await super().send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 542, in decorator
    result = await func(self, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 1018, in send_message
    return await self._send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 581, in _send_message
    result = await super()._send_message(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 736, in _send_message
    result = await self._post(
             ^^^^^^^^^^^^^^^^^
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
  File "/usr/local/lib/python3.11/site-packages/telegram/request/_baserequest.py", line 379, in _request_wrapper
    raise BadRequest(message)
telegram.error.BadRequest: Message to be replied not found
No error handlers are registered, logging exception.
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_application.py", line 1264, in process_update
    await coroutine
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_handlers/basehandler.py", line 157, in handle_update
    return await self.callback(update, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/main.py", line 97, in cmd_stats
    await update.message.reply_text(generate_stats(user_stats))
  File "/usr/local/lib/python3.11/site-packages/telegram/_message.py", line 1809, in reply_text
    return await self.get_bot().send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 2820, in send_message
    return await super().send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 542, in decorator
    result = await func(self, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 1018, in send_message
    return await self._send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 581, in _send_message
    result = await super()._send_message(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 736, in _send_message
    result = await self._post(
             ^^^^^^^^^^^^^^^^^
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
  File "/usr/local/lib/python3.11/site-packages/telegram/request/_baserequest.py", line 379, in _request_wrapper
    raise BadRequest(message)
telegram.error.BadRequest: Message to be replied not found
No error handlers are registered, logging exception.
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_application.py", line 1264, in process_update
    await coroutine
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_handlers/basehandler.py", line 157, in handle_update
    return await self.callback(update, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/main.py", line 91, in cmd_csv
    await update.message.reply_document(open(file_path, 'rb'))
  File "/usr/local/lib/python3.11/site-packages/telegram/_message.py", line 2302, in reply_document
    return await self.get_bot().send_document(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 2572, in send_document
    return await super().send_document(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 542, in decorator
    result = await func(self, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 1666, in send_document
    return await self._send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 581, in _send_message
    result = await super()._send_message(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 736, in _send_message
    result = await self._post(
             ^^^^^^^^^^^^^^^^^
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
  File "/usr/local/lib/python3.11/site-packages/telegram/request/_baserequest.py", line 379, in _request_wrapper
    raise BadRequest(message)
telegram.error.BadRequest: Message to be replied not found
No error handlers are registered, logging exception.
Traceback (most recent call last):
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_application.py", line 1264, in process_update
    await coroutine
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_handlers/basehandler.py", line 157, in handle_update
    return await self.callback(update, context)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/app/main.py", line 97, in cmd_stats
    await update.message.reply_text(generate_stats(user_stats))
  File "/usr/local/lib/python3.11/site-packages/telegram/_message.py", line 1809, in reply_text
    return await self.get_bot().send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 2820, in send_message
    return await super().send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 542, in decorator
    result = await func(self, *args, **kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 1018, in send_message
    return await self._send_message(
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_extbot.py", line 581, in _send_message
    result = await super()._send_message(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/_bot.py", line 736, in _send_message
    result = await self._post(
             ^^^^^^^^^^^^^^^^^
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
  File "/usr/local/lib/python3.11/site-packages/telegram/request/_baserequest.py", line 379, in _request_wrapper
    raise BadRequest(message)
telegram.error.BadRequest: Message to be replied not found
/app/main.py:166: PTBUserWarning: No `JobQueue` set up. To use `JobQueue`, you must install PTB via `pip install "python-telegram-bot[job-queue]"`.
  app.job_queue.run_repeating(process_save_jobs, interval=60, first=60)
Traceback (most recent call last):
  File "/app/main.py", line 180, in <module>
    main()
  File "/app/main.py", line 166, in main
    app.job_queue.run_repeating(process_save_jobs, interval=60, first=60)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'run_repeating'
/app/main.py:150: PTBUserWarning: No `JobQueue` set up. To use `JobQueue`, you must install PTB via `pip install "python-telegram-bot[job-queue]"`.
  app.job_queue.run_repeating(process_save_jobs, interval=60, first=60)
Traceback (most recent call last):
  File "/app/main.py", line 162, in <module>
    main()
  File "/app/main.py", line 150, in main
    app.job_queue.run_repeating(process_save_jobs, interval=60, first=60)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'run_repeating'
Traceback (most recent call last):
  File "/app/main.py", line 167, in <module>
    main()
  File "/app/main.py", line 152, in main
    jq = JobQueue()
         ^^^^^^^^^^
  File "/usr/local/lib/python3.11/site-packages/telegram/ext/_jobqueue.py", line 101, in __init__
    raise RuntimeError(
RuntimeError: To use `JobQueue`, PTB must be installed via `pip install "python-telegram-bot[job-queue]"`.
