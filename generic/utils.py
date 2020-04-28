from multiprocessing.pool import ThreadPool


def nonblocking(f, *args, **kwargs):
    ''' Run function f without blocking, returning an async_result handle

    Caller must call get() on the returned object to get the function return
    value. E.g.
    async_result = nonblocking(myFunction, 1, 2, 3, a='foo', b='bar')
    ...
    # Do other things
    ...
    myFunction_return_value = async_result.get()
    '''
    pool = ThreadPool(processes=1)
    async_result = pool.apply_async(f, args=args, kwds=kwargs)
    return async_result
