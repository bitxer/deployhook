from hook import init_app

app = init_app(config="hook.config.Development")

def main():
    app.run(host='0.0.0.0')


if __name__ == '__main__':
    main()
