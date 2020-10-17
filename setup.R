repos <- "http://cran.us.r-project.org"
libraries <- c("berryFunctions", "knitr", "vertexenum")
for (library in libraries)
{
    install.packages(library, repos = repos)
}
