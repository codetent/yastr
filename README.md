<div align="center">
  <img src="doc/logo.svg" width="100" /><br>
  
  # <b>Y</b>et <b>A</b>nother <b>S</b>imple <b>T</b>est <b>R</b>unner
  
  A simple test runner for just calling executables and generating reports.
  <br/><br/>

</div>

## Description

YASTR is a utility that gets the testing job quickly done without requiring a specific test framework. Instead just having an executable that shall be executed is enough.

In its simplest configuration, you just place your executable containing your test logic in a folder, create a configuration file to tell yastr how to execute it and you get a nice JUnit compatible output.

It is based on pytest, actually a testing framework for Python but not limited to. Thanks to it, yastr is able to run beside executables also Python tests and features like fixtures and markers can be reused.

## Features

YASTR provides the following:

- Running executables with arguments
- Settings environment variables
- Setting a timeout

And it supports everything that pytest offers:

- Creating Junit reports
- Adding markers
- Using fixtures
- Selecting specific tests
- Running tests written in Python
- And much more: https://docs.pytest.org/en/6.2.x/contents.html

## Documentation

- Quickstart: [doc/guide/quickstart.md](doc/guide/quickstart.md)
