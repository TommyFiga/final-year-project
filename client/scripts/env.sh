export CGO_CFLAGS="-I$(pwd)/tdlib/include"
export CGO_LDFLAGS="-L$(pwd)/tdlib/lib"
export LD_LIBRARY_PATH="$(pwd)/tdlib/lib"