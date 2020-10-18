# An Rscript to install all dependencies.
#
# Run with:
#
# $ Rscript setup.R
#
libraries <- c("berryFunctions", "knitr", "vertexenum")

repos <- "http://cran.us.r-project.org"
for (library in libraries)
{
    install.packages(library, repos = repos)
}
