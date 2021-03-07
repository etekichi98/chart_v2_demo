FROM python:3
USER root

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8
ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

RUN apt-get install -y vim
RUN pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install --upgrade Flask flask_cors mplfinance japanize-matplotlib
RUN cp -p /usr/local/lib/python3.9/site-packages/japanize_matplotlib/fonts/ipaexg.ttf /usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/fonts/ttf/
RUN echo "font.family : IPAexGothic">>/usr/local/lib/python3.9/site-packages/matplotlib/mpl-data/matplotlibrc
CMD ["python", "/root/opt/app.py"]
