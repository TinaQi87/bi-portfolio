# Base image with RStudio
FROM rocker/rstudio:latest

# Install system dependencies and R packages
RUN apt-get update && apt-get install -y \
    sudo \
    libcurl4-gnutls-dev \
    libcairo2-dev \
    libxt-dev \
    libssl-dev \
    libxml2-dev

# Install Shiny and other R packages
RUN R -e "install.packages(c('shiny', 'rmarkdown', 'tidyverse'))"