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
library(shinyBS)
library(stringr)
library(shinycssloaders)
library(highcharter)
library(formattable)
source("charts.R")

ui <- dashboardPage(skin = "green",
                    dashboardHeader(title = HTML("<a href='https://ealingrugby.co.uk/?page_id=12100'><img src='Trailfinders_rfc_logo.png' height='40px'></a> Ealing Rugby Men's: <b>Sam Lindsay</b>"),
                                    titleWidth = '95%'),
                    dashboardSidebar(
                      width = 200,
                      sidebarMenu(
                        menuItem("Game data", tabName = "data", icon = icon("table")),
                        menuItem("Stats",tabName = "stats", icon = icon("bar-chart-o")),
                        menuItem("Fixtures", icon = icon("calendar"),
                                 menuSubItem("1st", href = "https://ealingrugby.co.uk/?page_id=17590", icon = icon("external-link"), newtab = T),
                                 menuSubItem("2nd", href = "https://ealingrugby.co.uk/?page_id=17589", icon = icon("external-link"), newtab = T),
                                 menuSubItem("Exiles", href = "https://ealingrugby.co.uk/?page_id=17591", icon = icon("external-link"), newtab = T),
                                 menuSubItem("Evergreens", href = "https://ealingrugby.co.uk/?page_id=17592", icon = icon("external-link"), newtab = T))
                      )
                    ),
                    dashboardBody(
                      useShinyjs(),
                      tags$style(type="text/css",
                                 ".shiny-output-error { visibility: hidden; }",
                                 ".shiny-output-error:before { visibility: hidden; }"),
                      tabItems(
                        tabItem(
                          tabName = "data",
                          uiOutput("new_data"),
                          fluidRow(
                            box(
                              width = 12,
                              title = "Game history",
                              solidHeader = T,
                              status = "success",
                              fluidRow(
                                column(3, uiOutput("season_filter_input") %>%
                                         popify(title = "", placement = "top",
                                                content = "Select a specific season to view only games that year.")),
                                column(3, uiOutput("team_filter_input") %>%
                                         popify(title = "", placement = "top",
                                                content = "Select an Ealing team to view only games played for that team.")),
                                column(4, uiOutput("oppo_filter_input") %>%
                                         popify(title = "", placement = "top",
                                                content = "Select an opposition club to view only games played against that club (all squads).")),
                                column(2, radioGroupButtons("color_data_by", "Colour rows by...",
                                                            choices = c("Result", "Team"),
                                                            checkIcon = list(
                                                              yes = tags$i(class = "fa fa-check-square",
                                                                           style = "color: steelblue"),
                                                              no = tags$i(class = "fa fa-square-o",
                                                                          style = "color: steelblue"))
                                ) %>%
                                  popify(title = "", placement= "top", content = "Color rows by result <br> (W/L = green/red) <br> or team played for <br> (1st/2nd = green/orange)"))
                              ),
                              tags$hr(),
                              column(12, DT::dataTableOutput("dataTable") %>% withSpinner())
                            )
                          )
                        ),
                        tabItem(
                          tabName = "stats",
                          fluidRow(box(
                            title = "Summary stats",
                            width = 12,
                            collapsible = T,
                            solidHeader = T,
                            status = "warning",
                            #background = "yellow",
                            uiOutput("stats_filters"),
                            box(
                              title = "Quick stats",
                              width = 4,
                              solidHeader = T,
                              status = "success",
                              fluidRow(valueBoxOutput("game_count", width = 12)),
                              fluidRow(valueBoxOutput("minute_count", width = 12)),
                              fluidRow(valueBoxOutput("try_count", width = 6),
                                       valueBoxOutput("card_count", width = 6))
                            ),
                            box(
                              title = "Win percentage",
                              width = 3,
                              solidHeader = T,
                              status = "success",
                              fluidRow(valueBoxOutput("win_rate", width = 12)),
                              fluidRow(valueBoxOutput("win_rate_home", width = 12)),
                              fluidRow(valueBoxOutput("win_rate_away", width = 12))
                            ) %>%
                              popify(title = "", content = "Overall win rate (top) and separately at home and away.",
                                     placement = "top", trigger = "hover"),
                            box(
                              title = "Average score",
                              width = 3,
                              solidHeader = T,
                              status = "success",
                              fluidRow(valueBoxOutput("avg_score", width = 12)),
                              fluidRow(valueBoxOutput("avg_score_home", width = 12)),
                              fluidRow(valueBoxOutput("avg_score_away", width = 12))
                            ) %>%
                              popify(title = "", placement = "top", trigger = "hover",
                                     content = "Average points for and against in all games (top), home games and away games. Ealing score is shown first.")
                          )),
                          fluidRow(
                            box(
                              title = "Scores",
                              width = 6,
                              collapsible = T,
                              collapsed = T,
                              solidHeader = T,
                              status = "success",
                              fluidRow(column(6, highchartOutput("plot_scores")),
                                       column(3, highchartOutput("plot_games_team")))
                            ),
                            box(
                              title = "Cumulative games/minutes played",
                              width = 6,
                              collapsible = T,
                              collapsed = T,
                              solidHeader = T,
                              status = "success",
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
                              status = "success",
                              switchInput("toggle_by_team", "Break down by team", value = T, labelWidth = "150px", onStatus = "warning"),
                              br(),
                              uiOutput("plot_games")
                            )
                          )
                        )
                      ))
)
