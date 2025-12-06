# Troubleshooting Guide

Common issues and their solutions.

## LLM Connection Issues

### Problem: "LLM not configured" or "API key not set"

**Symptoms**:
- Document upload succeeds but no rules extracted
- Error: `LLM configuration file not found`
- Error: `AuthenticationError: api_key must be set`

**Solutions**:

**For Docker**:
```bash
# Ensure you're passing environment variables
docker run -p 8080:8080 \
  -e LLM_PROVIDER=ollama \
  -e LLM_MODEL=llama3 \
  -e LLM_BASE_URL=http://172.17.0.1:11434 \
  smart-memory
```

**For Local Development**:
1. Go to Dashboard → Admin page
2. Configure your LLM provider
3. Click "Test Connection" to verify
4. Click "Save Configuration"

---

### Problem: "Connection refused" to Ollama

**Symptoms**:
- Error: `[Errno 111] Connection refused`
- Error: `Name or service not known`

**Solutions**:

1. **Verify Ollama is running**:
   ```bash
   curl http://localhost:11434/api/tags
   ```
   Should return list of models.

2. **Check Ollama is accessible from Docker**:
   
   **On Linux**:
   ```bash
   # Use Docker bridge IP
   docker run -e LLM_BASE_URL=http://172.17.0.1:11434 ...
   ```
   
   **On Mac/Windows**:
   ```bash
   # Use host.docker.internal
   docker run -e LLM_BASE_URL=http://host.docker.internal:11434 ...
   ```
   
   **Alternative: Use network host mode (Linux only)**:
   ```bash
   docker run --network host \
     -e LLM_BASE_URL=http://localhost:11434 ...
   ```

3. **If Ollama is on another machine**:
   ```bash
   # Use the machine's IP address
   docker run -e LLM_BASE_URL=http://192.168.1.XXX:11434 ...
   ```

---

### Problem: API Key errors with OpenAI/Anthropic

**Symptoms**:
- Error: `Invalid API key`
- Error: `Unauthorized`

**Solutions**:

1. **Verify API key format**:
   - OpenAI: starts with `sk-`
   - Anthropic: starts with `sk-ant-`

2. **Check key is active**:
   - Test with curl:
     ```bash
     curl https://api.openai.com/v1/models \
       -H "Authorization: Bearer YOUR_API_KEY"
     ```

3. **Ensure key is passed correctly**:
   ```bash
   docker run -e LLM_API_KEY='your-actual-key' ...
   # Note: Use quotes if key contains special characters
   ```

---

## Docker Issues

### Problem: "Port already in use"

**Symptoms**:
- Error: `bind: address already in use`

**Solutions**:

1. **Find what's using port 8080**:
   ```bash
   lsof -i :8080
   # or
   netstat -tulpn | grep 8080
   ```

2. **Stop the conflicting process** or **use a different port**:
   ```bash
   docker run -p 9090:8080 ...  # Dashboard now on port 9090
   ```

---

### Problem: "Permission denied" mounting volume

**Symptoms**:
- Error: `mkdir: cannot create directory`
- Files not persisting

**Solutions**:

1. **Create directory first**:
   ```bash
   mkdir -p ./brain
   docker run -v $(pwd)/brain:/app/data ...
   ```

2. **Check permissions**:
   ```bash
   chmod 755 ./brain
   ```

---

### Problem: Docker build fails

**Symptoms**:
- Frontend build errors
- npm install failures

**Solutions**:

1. **Clear Docker cache**:
   ```bash
   docker build --no-cache -t smart-memory .
   ```

2. **Check Docker resources**:
   - Ensure you have at least 4GB RAM allocated to Docker

---

## Dashboard Issues

### Problem: Dashboard shows "Connection Error"

**Symptoms**:
- Frontend loads but shows API connection error
- Network tab shows 404 or CORS errors

**Solutions**:

**For Local Development** (`./scripts/start_dashboard.sh`):
1. Verify backend is running on port 8000:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. Check `vite.config.ts` has proxy configuration:
   ```typescript
   server: {
     proxy: {
       '/api': {
         target: 'http://localhost:8000',
         changeOrigin: true
       }
     }
   }
   ```

**For Docker**:
- This shouldn't happen. If it does, rebuild the image.

---

### Problem: "Failed to fetch" errors

**Symptoms**:
- Stats don't load
- Documents page empty

**Solutions**:

1. **Check backend logs**:
   ```bash
   # Docker
   docker logs <container-id>
   
   # Local
   tail -f /tmp/smartmemory_backend.log
   ```

2. **Verify API is responding**:
   ```bash
   curl http://localhost:8080/api/stats
   # or http://localhost:8000/api/stats for local dev
   ```

---

## MCP Setup Issues

### Problem: MCP server not appearing in client

**Symptoms**:
- SmartMemory tools not available in Claude Desktop
- No memory functionality

**Solutions**:

1. **Verify config file location**:
   - **Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. **Check JSON syntax**:
   ```bash
   # Validate JSON
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool
   ```

3. **Verify Python path**:
   ```bash
   # Should match path in config
   which python
   # or
   /path/to/SmartMemory/venv/bin/python --version
   ```

4. **Restart client completely**:
   - Quit Claude Desktop (Cmd+Q / Alt+F4)
   - Wait 5 seconds
   - Reopen

---

### Problem: "Module not found" errors

**Symptoms**:
- MCP server crashes on startup
- Import errors in logs

**Solutions**:

1. **Verify installation**:
   ```bash
   cd /path/to/SmartMemory
   source venv/bin/activate
   pip install -e .
   ```

2. **Check MCP config uses venv python**:
   ```json
   {
     "command": "/path/to/SmartMemory/venv/bin/python",
     "args": ["-m", "smart_memory.server"]
   }
   ```

---

## Rule Extraction Issues

### Problem: No rules extracted from document

**Symptoms**:
- Upload succeeds
- "0 rules extracted" message

**Possible Causes**:

1. **Document format not supported**:
   - Currently only PDF supported
   - Text must be extractable (not scanned image)

2. **LLM returned unexpected format**:
   - Check backend logs for LLM response
   - Try different model or temperature

3. **Document too short**:
   - LLM needs substantial content to extract rules

---

## Performance Issues

### Problem: Slow rule extraction

**Symptoms**:
- Upload takes >2 minutes
- Timeout errors

**Solutions**:

1. **Use faster model**:
   - Local: Try `qwen2.5-coder` instead of `llama3`
   - Cloud: Try `gpt-3.5-turbo` instead of `gpt-4`

2. **Reduce document size**:
   - Extract specific pages
   - Split large PDFs

3. **Increase timeout** (advanced):
   - Modify `rule_extractor.py` timeout settings

---

## Still Having Issues?

1. **Check logs**:
   - Docker: `docker logs <container-id>`
   - Local: `/tmp/smartmemory_backend.log`, `/tmp/smartmemory_frontend.log`

2. **Enable debug mode**:
   ```python
   # In rule_extractor.py
   import litellm
   litellm._turn_on_debug()
   ```

3. **Open an issue**:
   - [GitHub Issues](https://github.com/yourusername/SmartMemory/issues)
   - Include: OS, Docker version, full error message, logs
