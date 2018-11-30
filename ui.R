library(shiny)
library(shinydashboard)
library(DT)
library(dplyr)
library(tidyr)
library(readr)
library(lubridate)
library(data.table)
library(shinyWidgets)
library(shinyjs)
library(highcharter)
source("charts.R")

ui <- dashboardPage(
  dashboardHeader(title = "Rugby Results"),
  dashboardSidebar(
    sidebarMenu(
      menuItem("Data", tabName = "data", icon = icon("table")),
      menuItem("Stats", tabName = "stats", icon = icon("bar-chart-o"))
    )
  ),
  dashboardBody(
    useShinyjs(),
    tabItems(
      tabItem(
        tabName = "data",
        uiOutput("new_data"),
        fluidRow(
          box(
            width = 12,
            title = "Match History",
            collapsible = TRUE,
            status = "primary",
            fluidRow(
              column(6, uiOutput("season_filter_input")),
              column(6, uiOutput("team_filter_input"))
            ),
            column(12, DT::dataTableOutput("dataTable"))
            )
          )
        ),
      tabItem(
        tabName = "stats",
        fluidRow(box(
          title = "Summary Stats",
          width = 12,
          collapsible = T,
          status = "primary",
          uiOutput("stats_filters"),
          box(
            title = "Quick Stats",
            width = 4,
            solidHeader = T,
            status = "primary",
            fluidRow(valueBoxOutput("match_count", width = 12)),
            fluidRow(valueBoxOutput("minute_count", width = 12)),
            fluidRow(valueBoxOutput("try_count", width = 6),
                     valueBoxOutput("card_count", width = 6))
            ),
          box(
            title = "Win Percentage",
            width = 3,
            solidHeader = T,
            status = "primary",
            fluidRow(valueBoxOutput("win_rate", width = 12)),
            fluidRow(valueBoxOutput("win_rate_home", width = 12)),
            fluidRow(valueBoxOutput("win_rate_away", width = 12))
            ),
          box(
            title = "Average Scores*",
            width = 3,
            solidHeader = T,
            status = "primary",
            fluidRow(valueBoxOutput("avg_score", width = 12)),
            fluidRow(valueBoxOutput("avg_score_home", width = 12)),
            fluidRow(valueBoxOutput("avg_score_away", width = 12))
            )
          )),
      fluidRow(
        box(
          title = "Scores",
          width = 12,
          collapsible = T,
          collapsed = T,
          solidHeader = T,
          status = "primary",
          fluidRow(column(6, highchartOutput("plot_scores")),
                   column(3, highchartOutput("plot_games_team")))
          )
        ),
      fluidRow(
        box(
          title = "Cumulative games/minutes played",
          width = 12,
          collapsible = T,
          collapsed = T,
          solidHeader = T,
          status = "primary",
          fluidRow(
            column(
              6,
              radioGroupButtons("cum_games_or_mins", label = NULL, choices = c("Games", "Minutes"), justified = TRUE),
              conditionalPanel("input.cum_games_or_mins == 'Games'", highchartOutput("plot_cum_games")),
              conditionalPanel("input.cum_games_or_mins == 'Minutes'", highchartOutput("plot_cum_time"))
              ),
            column(
              6,
              box(
                width = 12,
                formattableOutput("table_win_rate")
                ),
              box(
                width = 12,
                formattableOutput("table_avg_score_team"),
                formattableOutput("table_avg_score_season")
                )
              )
            )
          )
        ),
      fluidRow(
        box(
          title = "Game count",
          width = 12,
          collapsible = T,
          collapsed = T,
          solidHeader = T,
          status = "primary",
          switchInput("toggle_by_team", "Break down by team", value = T, labelWidth = "150px", onStatus = "warning"),
          br(),
          uiOutput("plot_games")
          )
        )
      )
    ))
  )
