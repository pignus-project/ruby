# Makefile for source rpm: ruby
# $Id$
NAME := ruby
SPECFILE = $(firstword $(wildcard *.spec))

include ../common/Makefile.common
