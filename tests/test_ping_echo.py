"""Tests for PING and ECHO (these print instead of returning, so use capsys)."""


def test_ping_prints_pong(redis, capsys):
    redis.process_command("PING")
    
    captured = capsys.readouterr()
    assert("PONG" in captured.out)


def test_ping_with_args_is_rejected(redis, capsys):
    pout = redis.process_command("PING 4")
    assert(pout is None)
    
    captured = capsys.readouterr()
    assert("Invalid number of arguments for PING" in captured.out)
    


def test_echo_prints_message(redis, capsys):
    redis.process_command("ECHO Hello World!")
    
    captured = capsys.readouterr()
    assert("Hello World!" in captured.out)


def test_echo_without_args_is_rejected(redis, capsys):
    eout = redis.process_command("ECHO")
    assert(eout is None)
    
    captured = capsys.readouterr()
    assert("Invalid number of arguments for ECHO" in captured.out)
    
