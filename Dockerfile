FROM debian:latest
ENV apt="python-pip libsasl2-dev python-dev libldap2-dev libssl-dev git"
ENV git_url="https://github.com/matiasgonzalocalvo"
ENV challenge="ChallengeMercadoLibre2"
env python_challenge="challenge2.py"
RUN apt update ; apt install -y ${apt}
RUN git clone ${git_url}/${challenge}
WORKDIR ${challenge}
RUN pip install -r requirements.txt
CMD python ${python_challenge}
