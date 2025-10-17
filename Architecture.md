# TRNG-FastAPI — High Level Architecture

## Overview
This project generates high-quality entropy by combining two independent physical sources:
- Video entropy: live camera/video bitstream of a camera pointed at a very large tree
- SDR entropy: atmospheric noise from a remote SDR serving atmospheric noise via websocket

An Entropy Engine consumes both sources, applies a mixing function F(X, Y), and emits a pure entropy stream E.

## High-level Components
- Video Ingest
  - Captures live video frames, converts it to binary stream
  - Output: stream of video entropy chunks (X)
  - OPTIONAL - Lightweight pre-processing / whitening (frame diff, LSB extraction, optional compression)

- SDR Ingest
  - Opens websocket, reads data from stream, converts it to binary stream
  - Output: stream of SDR entropy chunks (Y)
  - OPTIONAL - Pre-processing (IQ demod, decimation, LSB/noise extraction)

- Entropy Engine
  - Receives X and Y (synchronized or buffered)
  - Applies Entropy Engine Logic F(X,Y) -> E
  - Exposes E to downstreams via API/stream
  - OPTIONAL Performs health checks and statistical tests on E

- API / Clients
  - FastAPI service exposing endpoints:
    - Streaming endpoint (WebSocket / gRPC) for live E
    - REST endpoints for health, metrics, sample pulls, audit logs
  - GOOD TO HAVE - Rate limiting, TLS

## Data Flow
- Check out Architecture.png

## Entropy Engine Logic F(X, Y)

