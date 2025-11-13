// NT_GLFW3W_PATCH: Override contrib.glfw3 helper to always write integral positions.
(function ntPatchGlfw3wGetPosition() {
  if (typeof Module === "undefined") {
    // eslint-disable-next-line no-global-assign
    Module = {};
  }

  const patchedSymbol = Symbol("nt_glfw3w_patched");

  function roundRectCoordinate(rect, primary, fallback) {
    if (typeof rect[primary] === "number") {
      return rect[primary];
    }
    if (typeof rect[fallback] === "number") {
      return rect[fallback];
    }
    return 0;
  }

  function wrapGetPosition(originalGetPosition) {
    if (typeof originalGetPosition !== "function" || originalGetPosition[patchedSymbol]) {
      return originalGetPosition;
    }

    const wrapped = function patchedGetPosition(glfwWindow, xPtr, yPtr) {
      if (!xPtr && !yPtr) {
        return originalGetPosition(glfwWindow, xPtr, yPtr);
      }

      const windowContexts =
        typeof GLFW3 !== "undefined" && GLFW3 && GLFW3.fWindowContexts
          ? GLFW3.fWindowContexts
          : null;
      const ctx = windowContexts ? windowContexts[glfwWindow] : null;
      const canvas = ctx && ctx.canvas;
      const rectReader =
        canvas && typeof canvas.getBoundingClientRect === "function"
          ? canvas.getBoundingClientRect.bind(canvas)
          : null;

      if (!rectReader) {
        return originalGetPosition(glfwWindow, xPtr, yPtr);
      }

      const rect = rectReader();
      const roundedX = Math.round(roundRectCoordinate(rect, "x", "left"));
      const roundedY = Math.round(roundRectCoordinate(rect, "y", "top"));

      if (xPtr) {
        HEAP32[xPtr >> 2] = roundedX;
      }
      if (yPtr) {
        HEAP32[yPtr >> 2] = roundedY;
      }
    };

    wrapped[patchedSymbol] = true;
    wrapped.original = originalGetPosition;
    return wrapped;
  }

  function installIntoImports(importObject) {
    if (!importObject || importObject[patchedSymbol]) {
      return;
    }
    if (typeof importObject.emglfw3w_get_position === "function") {
      importObject.emglfw3w_get_position = wrapGetPosition(importObject.emglfw3w_get_position);
    }
    importObject[patchedSymbol] = true;
  }

  function patchGetWasmImports() {
    if (typeof getWasmImports !== "function") {
      return false;
    }
    const originalGetWasmImports = getWasmImports;
    getWasmImports = function patchedGetWasmImports() {
      const imports = originalGetWasmImports.apply(this, arguments);
      if (imports && typeof imports === "object") {
        installIntoImports(imports.env);
        if (imports.wasi_snapshot_preview1 && imports.wasi_snapshot_preview1 !== imports.env) {
          installIntoImports(imports.wasi_snapshot_preview1);
        }
      }
      return imports;
    };
    return true;
  }

  if (!patchGetWasmImports()) {
    const preInitList = Module.preInit || (Module.preInit = []);
    preInitList.push(function ntFallbackInstallGlfwPatch() {
      if (typeof wasmImports === "object") {
        installIntoImports(wasmImports);
      }
    });
  }
})();
