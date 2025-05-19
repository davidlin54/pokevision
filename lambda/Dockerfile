FROM public.ecr.aws/lambda/python:3.9

# install git
RUN yum install -y git

# clone git repo
ARG GITHUB_TOKEN
RUN git clone https://${GITHUB_TOKEN}@github.com/davidlin54/pokevision.git /var/task

# change to work dir
WORKDIR /var/task

# run git pull
RUN git pull

# move model checkpoint files
COPY classes.json classes.json
COPY trained_model.data trained_model.data

# add AWS credentials
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_DEFAULT_REGION

ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION

ENV S3_MODEL_BUCKET=pokevision-model

# install pip dependencies
RUN pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# set the handler
CMD ["vision_eval.handler"]
