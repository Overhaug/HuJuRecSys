# SEBASTIAN OVERHAUG, adapted from script provided by CHRISTOPH TRATTNER
options(warn=-1)
library(RColorBrewer)
library(tm)
library(scales)
library(ggplot2)
library(stringr)
library(igraph)
library(reshape2)
library(Hmisc)
library(ellipse)
library(gridExtra)
library(PerformanceAnalytics)
library(reshape)
library(phytools)
library(caret)
library(Metrics)
library(elasticnet)
# parallel processing
# library(doMC)
library(rminer)
library(e1071)
options(scipen="100", digits="4")
# registerDoMC(cores = 12)


chart.Correlation <-
  function (R, histogram = TRUE, method=c("pearson", "kendall", "spearman"), ...)
  { # @author R Development Core Team
    # @author modified by Peter Carl
    # Visualization of a Correlation Matrix. On top the (absolute) value of the
    # correlation plus the result of the cor.test as stars. On botttom, the
    # bivariate scatterplots, with a fitted line
    
    x = checkData(R, method="matrix")
    
    if(missing(method)) method = method[1] #only use one
    
    # Published at http://addictedtor.free.fr/graphiques/sources/source_137.R
    panel.cor <- function(x, y, digits=4, prefix="", use="pairwise.complete.obs", meth = method, cex.cor, ...)
    {
      usr <- par("usr"); on.exit(par(usr))
      par(usr = c(0, 1, 0, 1))
      r <- cor(x, y, use=use, method=meth) # MG: remove abs here
      txt <- format(c(r, 0.123456789), digits=digits)[1]
      txt <- paste(prefix, txt, sep="")
      if(missing(cex.cor)) cex <- 0.8/strwidth(txt)
      
      test <- cor.test(as.numeric(x),as.numeric(y), method=meth)
      # borrowed from printCoefmat
      Signif <- symnum(test$p.value, corr = FALSE, na = FALSE,
                       cutpoints = c(0, 0.001, 0.01, 0.05, 0.1, 1),
                       symbols = c("***", "**", "*", ".", " "))
      # MG: add abs here and also include a 30% buffer for small numbers
      text(0.5, 0.5, txt, cex = cex * (abs(r) + .3) / 1.3)
      text(.8, .8, Signif, cex=cex, col=2)
    }
    f <- function(t) {
      dnorm(t, mean=mean(x), sd=sd.xts(x) )
    }
    
    #remove method from dotargs
    #dotargs <- list(...)
    #dotargs$method <- NULL
    #rm(method)
    
    hist.panel = function (x, ...=NULL ) {
      par(new = TRUE)
      hist(x,
           col = "light gray",
           probability = TRUE,
           axes = FALSE,
           main = "",
           breaks = "FD")
      lines(density(x, na.rm=TRUE),
            col = "red",
            lwd = 1)
      #lines(f, col="blue", lwd=1, lty=1) how to add gaussian normal overlay?
      rug(x)
    }
    
    # Draw the chart
    if(histogram)
      pairs(x, gap=0, lower.panel=panel.smooth, upper.panel=panel.cor, diag.panel=hist.panel)
    else
      pairs(x, gap=0, lower.panel=panel.smooth, upper.panel=panel.cor) 
  }


# helper function to calc means and so on
summarySE <- function(data=NULL, measurevar, groupvars=NULL, na.rm=FALSE,
                      conf.interval=.95, .drop=TRUE) {
  library(plyr)
  
  # New version of length which can handle NA's: if na.rm==T, don't count them
  length2 <- function (x, na.rm=FALSE) {
    if (na.rm) sum(!is.na(x))
    else       length(x)
  }
  
  # This does the summary. For each group's data frame, return a vector with
  # N, mean, and sd
  datac <- ddply(data, groupvars, .drop=.drop,
                 .fun = function(xx, col) {
                   c(N    = length2(xx[[col]], na.rm=na.rm),
                     mean = mean   (xx[[col]], na.rm=na.rm),
                     sd   = sd     (xx[[col]], na.rm=na.rm)
                   )
                 },
                 measurevar
  )
  
  # Rename the "mean" column    
  datac <- rename(datac, c("mean" = measurevar))
  
  datac$se <- datac$sd / sqrt(datac$N)  # Calculate standard error of the mean
  
  # Confidence interval multiplier for standard error
  # Calculate t-statistic for confidence interval: 
  # e.g., if conf.interval is .95, use .975 (above/below), and use df=N-1
  ciMult <- qt(conf.interval/2 + .5, datac$N-1)
  datac$ci <- datac$se * ciMult
  
  return(datac)
}

cor.mtest <- function(mat, conf.level = 0.95){
  mat <- as.matrix(mat)
  n <- ncol(mat)
  p.mat <- lowCI.mat <- uppCI.mat <- matrix(NA, n, n)
  diag(p.mat) <- 0
  diag(lowCI.mat) <- diag(uppCI.mat) <- 1
  for(i in 1:(n-1)){
    for(j in (i+1):n){
      tmp <- cor.test(mat[,i], mat[,j], conf.level = conf.level)
      p.mat[i,j] <- p.mat[j,i] <- tmp$p.value
      lowCI.mat[i,j] <- lowCI.mat[j,i] <- tmp$conf.int[1]
      uppCI.mat[i,j] <- uppCI.mat[j,i] <- tmp$conf.int[2]
    }
  }
  return(list(p.mat, lowCI.mat, uppCI.mat))
}

no <- function(x) {
  xx <- NULL
  
  for (i in 1:length(x)) {
    l<- x[[i]]
    
    if (l >= 0 & l < .20) {
      xx<- c(xx, 1)
      #print(1)
    } else if (l >= .20 & l < .40) {
      xx<-c(xx, 2)
    } else if (l >= .40 & l < .60) {
      xx<-c(xx, 3) 
    } else if (l >= .60 & l < .80) {
      xx<- c(xx, 4)
    } else {
      xx<- c(xx, 5)
    }
  }
  return(xx)
  
}

# basics
demo <- read.table(file = 'E:/data/logs/parsed/SIM-online-survey-out-demo.csv', sep = '\t', header = TRUE)
demo1 <- subset(demo, passed=='TRUE')
demo1 <- subset(demo1, finished=='TRUE')
# all
nrow(demo)
# passed
nrow(demo1)

data <- read.table(file = 'E:/data/logs/parsed/SIM-online-survey-out-pairs.csv', sep = '\t', header = TRUE)
data1 <- subset(data, passed=='TRUE')
data1 <- subset(data, rand!=step)

# all
nrow(data)
# passed
nrow(data1)

# DEMO DATA

demo <- read.table(file = 'E:/data/logs/parsed/SIM-online-survey-out-demo.csv', sep = '\t', header = TRUE)
demo <- na.omit(subset(demo, passed=='TRUE'))

m1 <- mean(abs(demo$newsws))
d1 <- ggplot(demo, aes(newsws))  + 
  geom_bar(alpha=.99)  +  theme(axis.text.y = element_text(colour="black"))+
  xlab("News Website Visits") + theme(axis.text.x = element_text(angle = 90, hjust = 1,size=8,colour="black"))+
  ylab("Count") + scale_x_discrete(name ="News website visits", 
                                   limits=c("Daily","Once a week","Once a month","Every 3 months","Hardly use them"))
# annotate("text", x = m1+1, y = 11, label = paste("Median:",round(m1,digits = 2)))+
# geom_vline(aes(xintercept=m1),linetype="dashed",color="black", size=1)+ scale_colour_grey() 
#d1


m2 <- mean(abs(demo$days_news))
d2 <- ggplot(demo, aes(days_news))  + 
  geom_bar(alpha=.99)  +  ylab("Count") +theme(axis.text.y = element_text(colour="black")) +
  xlab("Num. Days Reads News \n (per week)") + theme(axis.text.x = element_text(size=8,colour="black"))+
  scale_x_continuous(breaks = c(0, 1,2,3,4,5, 6,7))  + scale_colour_grey() 
#d2


d8 <- ggplot(demo, aes(gender))  + 
  geom_bar(alpha=.99)  +  theme(axis.text.y = element_text(colour="black"))+
  ylab("Count") +theme(axis.text.x = element_text(size=8,colour = "black"))+
  xlab("Gender") + scale_colour_grey() 
#d8

d9 <- ggplot(demo, aes(age))  + 
  #xlim(0, 40)  + 
  geom_bar(alpha=.99)  +  
  ylab("Count") +theme(axis.text.x = element_text(angle = 90, hjust = 1,size=8,colour="black"))+theme(axis.text.y = element_text(colour="black"))+
  xlab("Age")+ scale_colour_grey() +scale_x_discrete(limits=c("18-24","25-34","35-44","45-54",">55"))



d9


#library(gridExtra)
#grid.arrange(d1, d2, d8, d9, ncol=2, nrow =2)

library(ggpubr)
pdf(height=4, width=6, file="E:/data/logs/parsed/figs/demos.pdf")
ggarrange(d1, d2, d8, d9, 
          labels = c("A", "B", "C","D"),
          ncol = 2, nrow = 2)
dev.off()


# CUE usage

data <- read.table(file = 'E:/data/logs/parsed/SIM-online-survey-out-pairs.csv', sep = '\t', header = TRUE)
data <- subset(data, passed=='TRUE')
data <- subset(data, rand!=step)

data3 <- melt(data.frame(data$title,data$image,data$text,data$subcat,data$author,data$author_bio,data$datetime,data$sentiment))
data3$variable <- as.factor(data3$variable)

levels(data3$variable)[levels(data3$variable)=="data.title"] <-"Title"
levels(data3$variable)[levels(data3$variable)=="data.image"] <-"Image"
levels(data3$variable)[levels(data3$variable) == "data.text"] <- "Body Text"
levels(data3$variable)[levels(data3$variable) == "data.subcat"] <- "Subcat"
levels(data3$variable)[levels(data3$variable) == "data.author"] <- "Author"
levels(data3$variable)[levels(data3$variable) == "data.author_bio"] <- "Author Bio"
levels(data3$variable)[levels(data3$variable) == "data.datetime"] <- "Date of Pub"
levels(data3$variable)[levels(data3$variable) == "data.sentiment"] <- "Sentiment"

tgc <- summarySE(data3, measurevar="value", groupvars=c("variable"))
tgc


a1<-ggplot(tgc, aes(x=variable, y=value)) + 
  geom_errorbar(aes(ymin=value-se, ymax=value+se), width=.1) +theme(axis.text.y = element_text(colour="black",size=9))+
  theme(axis.text.x = element_text(angle = 90, hjust = 1,size=9,colour = "black"))+ theme(legend.position="none")+
  geom_point(size=4) + ylab("Cue Usage")+ xlab("Information Cue")
a1



data3 <- melt(data.frame(data$title,data$image,data$text,data$subcat,data$author,data$datetime,data$author_bio,data$sentiment))
data3$variable <- as.factor(data3$variable)

data3 <- melt(data.frame(data$title,data$image,data$text,data$subcat,data$author,data$datetime,data$author_bio,data$sentiment))
data3$variable <- as.factor(data3$variable)

levels(data3$variable)[levels(data3$variable)=="data.title"] <-"Title"
levels(data3$variable)[levels(data3$variable)=="data.image"] <-"Image"
levels(data3$variable)[levels(data3$variable) == "data.text"] <- "Body Text"
levels(data3$variable)[levels(data3$variable) == "data.subcat"] <- "Subcat"
levels(data3$variable)[levels(data3$variable) == "data.author"] <- "Author"
levels(data3$variable)[levels(data3$variable) == "data.author_bio"] <- "Author Bio"
levels(data3$variable)[levels(data3$variable) == "data.datetime"] <- "Date of Pub"
levels(data3$variable)[levels(data3$variable) == "data.sentiment"] <- "Sentiment"

m = aov(formula= value~variable,data=data3)
anova(m)
TKHSD_Tc <- TukeyHSD(m,conf.level = 0.95)
TK<-(TKHSD_Tc)
TK_data<-as.data.frame(TK[1:1])
TK_data <- cbind(rownames(TK_data), TK_data)
rownames(TK_data) <- NULL
names(TK_data) = c("pair","diff","lwr","upr","p.adj")



# Plot pairwise TukeyHSD comparisons and color by significance level
a2<-ggplot(TK_data, aes(colour=cut(`p.adj`, c(-1,0, 0.01, 0.05, 1), 
                                   label=c("p<0.001","p<0.01","p<0.05","Non-Sig")))) +
  geom_hline(yintercept=0, lty="11", colour="grey30") +theme_bw()+
  geom_errorbar(aes(pair, ymin=lwr, ymax=upr), width=0.2) +
  geom_point(aes(pair, diff)) +theme(axis.text.y = element_text(colour="black",size=9))+
  labs(colour="")+theme(axis.text.x = element_text(angle = 90, hjust = 1,size=6,colour = "black")) +xlab("Pair")+ ylab("Difference") +  scale_colour_grey()
a2

# Plot pairwise TukeyHSD comparisons and color by significance level
#a2<-ggplot(TK_data, aes(colour=cut(`p.adj`, c(-1,0, 0.01, 0.05, 1), 
#                                   label=c("p<0.001","p<0.01","p<0.05","Non-Sig")))) +
#  geom_hline(yintercept=0, lty="11", colour="grey30") +  theme_bw()+
#  geom_errorbar(aes(pair, ymin=lwr, ymax=upr), width=0.2) +
#  geom_point(aes(pair, diff)) +theme(axis.text.y = element_text(colour="black",size=9))+
#  labs(colour="")+theme(axis.text.x = element_text(angle = 90, hjust = 1,size=9,colour = "black")) +xlab("Pair")+ ylab("Difference")+
  # geom_bar(stat="identity")+ scale_fill_grey(start = 0, end = .9) # ,colour="black"
#a2

library(ggpubr)
pdf(height=4, width=8, file="E:/data/logs/parsed/figs/study-cue-use.pdf")
ggarrange(a1,a2, 
          labels = c("A", "B"),
          ncol = 2, nrow = 1)
dev.off()
# ^ adjust text



# feature correlation
data <- read.table(file = 'E:/data/logs/parsed/SIM-online-survey-out-pairs.csv', sep = '\t', header = TRUE)
data <- na.omit(data)
data <- subset(data, passed=='TRUE')
data <- subset(data, rand!=step)


data <- subset(data, select= c(rating,all,title_lev, title_jw, title_lcs, title_bigram, title_lda, text_sent, text_lda, text_tfidf, text50_tfidf, 
                               embeddings, brightness, sharpness, contrast, colorfulness, entropy, bio_tfidf, bio_lda, author_jacc, daydist, subcat_jacc))


names(data) <- c("User:Rating", # user study sim
                 "All",
                 "Title:LEV", 
                 "Title:JW",
                 "Title:LCS",
                 "Title:BI",
                 "Title:LDA",
                 "BodyText:Sent","BodyText:LDA", "BodyText:TFIDF", "BodyText:50TFIDF",
                 "Image:EMB","Image:BR","Image:SH","Image:CO","Image:COL","Image:EN",
                 "AuthorBio:TFIDF", "AuthorBio:LDA",
                 "Author:Jacc",
                 "Date:ND",
                 "Subcat:Jacc"
)

library(corrplot)
M <- cor(data,method="spearman")

co <- rcorr(as.matrix(data), type="spearman")
d<-co[["P"]]
#M
#p.mat <- cor.mtest(data)
#col <- colorRampPalette(c("#BB4444", "#EE9988", "#FFFFFF", "#77AADD", "#4477AA"))
#corrplot(M, method = "color", col = col(200),
#         type = "upper",  number.cex = .5,
#         addCoef.col = "black", # Add coefficient of correlation
#         tl.col = "black", tl.srt = 90, # Text label color and rotation
#         # Combine with significance
#         p.mat = p.mat, sig.level = 0.01, insig = "blank", 
#         # hide correlation coefficient on the principal diagonal
#         diag = FALSE)


corrmatrix <- cor(data, method="spearman", use="complete")
cor.mtest <- function(mat, conf.level = 0.95){
  mat <- as.matrix(mat)
  n <- ncol(mat)
  p.mat <- lowCI.mat <- uppCI.mat <- matrix(NA, n, n)
  diag(p.mat) <- 0
  diag(lowCI.mat) <- diag(uppCI.mat) <- 1
  for(i in 1:(n-1)){
    for(j in (i+1):n){
      tmp <- cor.test(mat[,i], mat[,j], conf.level = conf.level)
      p.mat[i,j] <- p.mat[j,i] <- tmp$p.value
      lowCI.mat[i,j] <- lowCI.mat[j,i] <- tmp$conf.int[1]
      uppCI.mat[i,j] <- uppCI.mat[j,i] <- tmp$conf.int[2]
    }
  }
  return(list(p.mat, lowCI.mat, uppCI.mat))
}
res1 <- cor.mtest(corrmatrix,0.95)
col1 <- colorRampPalette(brewer.pal(9,"BrBG"))

library(corrplot)

#pdf(height=5.5, width=5.6, file="E:/data/logs/parsed/figs/epj-kochbar-corr.pdf")
#corrplot(corrmatrix, method="color",tl.col="black",tl.cex = 0.3,tl.offset = 0) 
corrplot(corrmatrix,method = "square", tl.col = "black", tl.cex = 0.8, ,tl.offset = 0.1, p.mat = d, sig.level = 0.05, insig = "pch", pch.cex = 0.8, col = col1(10))
#dev.off()

chart.Correlation(data,method = c("spearman"))
r<-rcorr(as.matrix(data), type="spearman")
#r$r
#r$P


all_set <- data$All
rating_set <- data$`User:Rating`
title_set <- (data$`Title:LEV`+data$`Title:JW`+data$`Title:LEV`+data$`Title:BI`+data$`Title:LDA`)/5.0
img_set <- (data$`Image:EMB`+data$`Image:BR`+data$`Image:SH`+data$`Image:CO`+data$`Image:COL`+data$`Image:EN`)/6.0
bodytext_set <- (data$`BodyText:TFIDF`+data$`BodyText:50TFIDF`+data$`BodyText:LDA`)/3.0
sent_set <- (data$`BodyText:Sent`)/1.0
authorbio_set <- (data$`AuthorBio:TFIDF`+data$`AuthorBio:LDA`)/2.0
author_set <- (data$`Author:Jacc`)/1.0
date_set <- (data$`Date:ND`)/1.0
subcat_set <- (data$`Subcat:Jacc`)/1.0

dat <- data.frame(rating_set,subcat_set,title_set,img_set,author_set,date_set,bodytext_set,sent_set,authorbio_set,all_set)


names(dat) <- c("\nHuman \n Judgment", 
                "Subcat",
                "Title", 
                "Image",
                "Author",
                "Date",
                "BodyText",
                "Sentiment",
                "AuthorBio",
                "All"
)

r<-rcorr(as.matrix(dat), type="spearman")
#r$r
#r$P

chart.Correlation(dat,method = c("spearman"))




# sim rating prediction 
data <- read.table(file = 'E:/data/logs/parsed/SIM-online-survey-out-pairs.csv', sep = '\t', header = TRUE)
data <- na.omit(data)
data <- subset(data, passed=='TRUE')
data <- subset(data, rand!=step)


data <- subset(data, select= c(rating#,all
                               ,title_lev, title_jw, title_lcs, title_bigram, title_lda, text_sent, text_lda, text_tfidf, text50_tfidf, 
                               embeddings, brightness, sharpness, contrast, colorfulness, entropy, bio_tfidf, bio_lda, author_jacc, daydist, subcat_jacc,
                               age,gender,newsws,days_news))


names(data) <- c("User:Rating", # user study sim
                # "All",
                 "Title:LEV", 
                 "Title:JW",
                 "Title:LCS",
                 "Title:BI",
                 "Title:LDA",
                 "BodyText:Sent","BodyText:LDA", "BodyText:TFIDF", "BodyText:50TFIDF",
                 "Image:EMB","Image:BR","Image:SH","Image:CO","Image:COL","Image:EN",
                 "AuthorBio:TFIDF", "AuthorBio:LDA",
                 "Author:Jacc",
                 "Date:ND",
                 "Subcat:Jacc",
                "age", "gender", "newsws", "days_news"
)

results_lm <- NULL
results_rf <- NULL
results_rg <- NULL
results_lo <- NULL
results_xg <- NULL
results_null <- NULL
results_rnd <- NULL



mySummary <- function (data,
                       lev = NULL,
                       model = NULL) {
  c(RMSE=sqrt(mean((data$obs-data$pred)^2)),
    Rsquared=summary(lm(pred ~ obs, data))$r.squared,
    MAE=mean(abs(data$obs-data$pred)),
  #  MdAE=median(abs(data$obs-data$pred)),
  # SMAPE=mean(2*abs(data$obs-data$pred)/(abs(data$obs)+ abs(data$pred))),
  r = rcorr(as.matrix(data.frame(data$obs,data$pred)), type="pearson")$r
  )
}

#mySummary <- function (data,
#                       lev = NULL,
#                       model = NULL) {
#  c(RMSE=sqrt(mean((data$obs-data$pred)^2)),
   # Rsquared=summary(lm(pred ~ obs, data))$r.squared,
 #   MAE=mean(abs(data$obs-data$pred))
   # MdAE=median(abs(data$obs-data$pred)),
   # SMAPE=mean(2*abs(data$obs-data$pred)/(abs(data$obs)+ abs(data$pred)))
#  )
#}

cv <- trainControl(method = "cv", 5, summaryFunction=mySummary, 
                   allowParallel = TRUE,
                   savePredictions = TRUE)

options(scipen="100", digits="6")
# RF MODEL
results_rf = NULL

model <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`,
  data = data,
  method = "rf",
  trControl = cv,
  importance = TRUE,
  ntree = 100
)
rcorr(as.matrix(data.frame(model$pred$pred,model$pred$obs)), type="spearman")$r
results_rf<-rbind(results_rf, cbind(var="RF-ALL", subset(model$results, mtry == model$bestTune$mtry)))


# LM MODEL

model <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`,
  data = data,
  method = "lm",
  trControl = cv,
  importance = TRUE
)
rcorr(as.matrix(data.frame(model$pred$pred,model$pred$obs)), type="spearman")$r
results_lm<-rbind(results_lm, cbind(var="LM-ALL", model$results))


# Mean model
results_null = NULL
model_null = NULL
model_null <- train(
  `User:Rating` ~ rep(1.709, 2169),
  data = data,
  method = "lm",
  trControl =cv
)

rcorr(as.matrix(data.frame(model_null$pred$pred,model_null$pred$obs)), type="spearman")$r
results_null<-rbind(results_null, cbind(var="MEAN-ALL", model_null$results))


# Rand model
results_rnd = NULL
model_rnd <- train(
  `User:Rating` ~ runif(2169, 1, 5),
  data = data,
  method = "lm",
  trControl =cv
)
rcorr(as.matrix(data.frame(model_rnd$pred$pred,model_rnd$pred$obs)), type="spearman")$r
results_rnd<-rbind(results_rnd, cbind(var="RAND-ALL", model_rnd$results))


# Lasso
model_lasso <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`,  data = data,
  method = "lasso",
  trControl = cv
)
rcorr(as.matrix(data.frame(model_lasso$pred$pred,model_lasso$pred$obs)), type="spearman")$r
results_lo<-rbind(results_lo, cbind(var="LS-ALL", subset(model_lasso$results, fraction == model_lasso$bestTune$fraction)))


# xg Model
results_xg = NULL

model <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`,
  data = data,
  method = "xgbTree",
  trControl = cv
)
rcorr(as.matrix(data.frame(model$pred$pred,model$pred$obs)), type="spearman")$r
results_xg<-rbind(results_xg, cbind(var="XG-ALL", subset(model$results, eta == model$bestTune$eta)))



# Ridge Model

model_rg = NULL
model_rg <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`, data = data,
  method = "ridge",
  trControl = cv
)
rcorr(as.matrix(data.frame(model_rg$pred$pred,model_rg$pred$obs)), type="spearman")$r
results_rg<-rbind(results_rg, cbind(var="RG-ALL", subset(model_rg$results, lambda == model_rg$bestTune$lambda)))

wilcox.test(model_rg$pred$pred, model_lasso$pred$pred)

# RESULTS models
results_lm 
results_rf 
results_rg 
results_lo 
results_xg 
results_null 
results_rnd 


###### VARIMP PLOT
vI <- varImp(model_rg,scale = TRUE)
vI
write.table(vI$importance, file="E:/data/logs/parsed/results/ig3.csv", quote=FALSE, sep='\t', row.names = TRUE)

### REMEMBER TO DO IT Manual
ig_data <- read.table(file = 'E:/data/logs/parsed/results/ig.csv', sep = '\t', header = TRUE)

v1 <- ggplot(ig_data, aes(x=reorder(Name, -Value), y=Value,fill=Category)) +  theme_bw()+
  geom_bar(stat="identity")+ # ,colour="black"
  xlab("Feature (Sim. Metric)") + ylab("Importance") +  theme(axis.text.x = element_text(angle = 90, hjust = 1,size=6))+
  theme(axis.text=element_text(size=2))+ 
  #scale_y_continuous(labels = function(x)paste0(x,".00"))+ 
  # ggtitle("Allrecips.com - Num. Ratings/Commments within 7 days") +scale_y_continuous(breaks= pretty_breaks())+theme(axis.text.x = element_text(size=8,colour = "black"))
  theme(plot.title = element_text(hjust = 0.5))+ theme(axis.text.y = element_text(size=5,colour="black"))+ theme(axis.text.x = element_text(size=6,colour="black"))+
  theme(legend.justification=c(0,0), 
        legend.position=c(0.73,0.20),
        legend.text=element_text(size=4),
        legend.key = element_blank(),
        legend.key.height = unit(0.2, "cm"),
        legend.key.width = unit(0.2, "cm"),
        legend.title=element_text(size=8),
        axis.title=element_text(size=9),
        legend.background = element_blank(),axis.text=element_text(size=2))+guides(fill=guide_legend(title="Feature Set",size=6))+ scale_fill_grey(start = 0, end = .9)
# theme(legend.position="none")
#scale_y_continuous(labels =NotFancy)#+scale_y_continuous(breaks= pretty_breaks())
v1

ggsave(file="E:/data/logs/parsed/figs/ig2.pdf", v1,width = 8, height = 5.5, units = "cm") #saves g


#### Prediction with user characteristics/demographics

# Sim rating prediction 
data <- read.table(file = 'E:/data/logs/parsed/SIM-online-survey-out-pairs.csv', sep = '\t', header = TRUE)
data <- na.omit(data)
data <- subset(data, passed=='TRUE')
data <- subset(data, rand!=step)


data <- subset(data, select= c(rating#,all
                               ,title_lev, title_jw, title_lcs, title_bigram, title_lda, text_sent, text_lda, text_tfidf, text50_tfidf, 
                               embeddings, brightness, sharpness, contrast, colorfulness, entropy, bio_tfidf, bio_lda, author_jacc, daydist, subcat_jacc,
                               age,gender,newsws,days_news))


names(data) <- c("User:Rating", # user study sim
                 # "All",
                 "Title:LEV", 
                 "Title:JW",
                 "Title:LCS",
                 "Title:BI",
                 "Title:LDA",
                 "BodyText:Sent","BodyText:LDA", "BodyText:TFIDF", "BodyText:50TFIDF",
                 "Image:EMB","Image:BR","Image:SH","Image:CO","Image:COL","Image:EN",
                 "AuthorBio:TFIDF", "AuthorBio:LDA",
                 "Author:Jacc",
                 "Date:ND",
                 "Subcat:Jacc","age","gender","newsws","days_news"
)


results_rg <- NULL



model_all_chars <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`+age+gender+newsws+days_news,data = data,
  method = "ridge",
  trControl = cv
)
rcorr(as.matrix(data.frame(model_all_chars$pred$pred,model_all_chars$pred$obs)), type="spearman")$r
results_rg<-rbind(results_rg, cbind(var="ALL", subset(model_all_chars$results, lambda == model_all_chars$bestTune$lambda)))

model_age <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`+age,data = data,
  method = "ridge",
  trControl = cv
)
rcorr(as.matrix(data.frame(model_age$pred$pred,model_age$pred$obs)), type="spearman")$r
results_rg<-rbind(results_rg, cbind(var="AGE", subset(model_age$results, lambda == model_age$bestTune$lambda)))


model_gender <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`+gender,data = data,
  method = "ridge",
  trControl = cv
)
rcorr(as.matrix(data.frame(model_gender$pred$pred,model_gender$pred$obs)), type="spearman")$r
results_rg<-rbind(results_rg, cbind(var="GENDER", subset(model_gender$results, lambda == model_gender$bestTune$lambda)))


model_newsws <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`+newsws,data = data,
  method = "ridge",
  trControl = cv
)
rcorr(as.matrix(data.frame(model_newsws$pred$pred,model_newsws$pred$obs)), type="spearman")$r
results_rg<-rbind(results_rg, cbind(var="newsws", subset(model_newsws$results, lambda == model_newsws$bestTune$lambda)))

model_days <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`+
    `BodyText:Sent` + `BodyText:LDA` + `BodyText:TFIDF` + `BodyText:50TFIDF` +
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`+
    `AuthorBio:TFIDF` + `AuthorBio:LDA` +
    `Author:Jacc`+
    `Date:ND`+
    `Subcat:Jacc`+days_news,data = data,
  method = "ridge",
  trControl = cv
)
rcorr(as.matrix(data.frame(model_days$pred$pred,model_days$pred$obs)), type="spearman")$r
results_rg<-rbind(results_rg, cbind(var="days_news", subset(model_days$results, lambda == model_days$bestTune$lambda)))

results_rg


# Prediction results per CUE

results_title <- NULL
results_image <- NULL
results_bodytext <- NULL
results_subcat <- NULL
results_author <- NULL
results_authorbio <- NULL
results_date <- NULL
results_sent <- NULL

# per CUE

#### Title
model_title <- train(
  `User:Rating`~
    `Title:LEV`+ 
    `Title:JW`+
    `Title:LCS`+
    `Title:BI`+
    `Title:LDA`,  
  data = subset(data,select= c(`User:Rating`,`Title:LEV`, 
                               `Title:JW`,
                               `Title:LCS`,
                               `Title:BI`,
                               `Title:LDA`)),
  method = "ridge",
  trControl = cv
)
results_title<-rbind(results_title, cbind(var="Title", subset(model_title$results, lambda == model_title$bestTune$lambda)))


#### Image
model_image <- train(
  `User:Rating`~
    `Image:EMB`+`Image:BR`+`Image:SH`+`Image:CO`+`Image:COL`+`Image:EN`,  
  data = subset(data,select= c(`User:Rating`, `Image:EMB`,`Image:BR`,`Image:SH`,`Image:CO`,`Image:COL`,`Image:EN`)),
  method = "ridge",
  trControl = cv
)

results_image<-rbind(results_image, cbind(var="Image", subset(model_image$results, lambda == model_image$bestTune$lambda)))


#### Body text
model_bodytext <- train(
  `User:Rating`~
    `BodyText:LDA`+`BodyText:TFIDF`+`BodyText:50TFIDF`,  data = subset(data,select= c(`User:Rating`, `BodyText:LDA`, `BodyText:TFIDF`, `BodyText:50TFIDF`)),
  method = "ridge",
  trControl = cv
)
results_bodytext<-rbind(results_bodytext, cbind(var="Body text", subset(model_bodytext$results, lambda == model_bodytext$bestTune$lambda)))


#### Subcategory
model_subcat <- train(
  `User:Rating`~
    `Subcat:Jacc`,  data = subset(data,select= c(`User:Rating`, `Subcat:Jacc`)),
  method = "lm",
  trControl = cv
)
results_subcat<-rbind(results_subcat, cbind(var="Subcategory", model_subcat$results))

#### Author
model_author <- train(
  `User:Rating`~
    `Author:Jacc`,  data = subset(data,select= c(`User:Rating`, `Author:Jacc`)),
  method = "lm",
  trControl = cv
)
results_author<-rbind(results_author, cbind(var="Authors", model_author$results))

#### Author bio
model_authorbio <- train(
  `User:Rating`~
    `AuthorBio:LDA`+`AuthorBio:TFIDF`,  data = subset(data,select= c(`User:Rating`, `AuthorBio:LDA`, `AuthorBio:TFIDF`)),
  method = "ridge",
  trControl = cv
)
results_authorbio<-rbind(results_authorbio, cbind(var="Author bio", subset(model_authorbio$results, lambda == model_authorbio$bestTune$lambda)))

#### Date of publication
model_date <- train(
  `User:Rating`~
    `Date:ND`,  data = subset(data,select= c(`User:Rating`, `Date:ND`)),
  method = "lm",
  trControl = cv
)
results_date<-rbind(results_date, cbind(var="Date", model_date$results))

### Sentiment
results_sent = NULL
model_sent <- train(
  `User:Rating`~
    `BodyText:Sent`,  data = subset(data,select= c(`User:Rating`, `BodyText:Sent`)),
  method = "lm",
  trControl = cv
)
results_sent<-rbind(results_sent, cbind(var="Sentiment", model_sent$results))

options(scipen="100", digits="4")

results_title 
rcorr(as.matrix(data.frame(model_title$pred$pred,model_title$pred$obs)), type="spearman")$r

results_image 
rcorr(as.matrix(data.frame(model_image$pred$pred,model_image$pred$obs)), type="spearman")$r

results_bodytext
rcorr(as.matrix(data.frame(model_bodytext$pred$pred,model_bodytext$pred$obs)), type="spearman")$r

results_subcat
rcorr(as.matrix(data.frame(model_subcat$pred$pred,model_subcat$pred$obs)), type="spearman")$r

results_author
rcorr(as.matrix(data.frame(model_author$pred$pred,model_author$pred$obs)), type="spearman")$r

results_authorbio
rcorr(as.matrix(data.frame(model_authorbio$pred$pred,model_authorbio$pred$obs)), type="spearman")$r

results_date 
rcorr(as.matrix(data.frame(model_date$pred$pred,model_date$pred$obs)), type="spearman")$r

results_sent
rcorr(as.matrix(data.frame(model_sent$pred$pred, model_sent$pred$obs)), type="spearman")$r


wilcox.test(model_rg$pred$pred, model_age$pred$pred)

wilcox.test(model_rg$pred$pred, model_bodytext$pred$pred)

