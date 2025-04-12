import pytest
import typing
def skip_if_no_capture(request) -> bool|typing.NoReturn:
    capture_option = request.config.option.capture
    if capture_option != "no":
        pytest.skip("The -s flag is not set. Test requires interaction.")
        assert False, "wtf"
    return False