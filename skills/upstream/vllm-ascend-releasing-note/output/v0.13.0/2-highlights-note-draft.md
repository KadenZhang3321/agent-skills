This is the 2nd release candidate of v0.13.0 for vLLM Ascend. Please follow the [official doc](https://docs.vllm.ai/projects/ascend/en/latest) to get started.

### Highlights

**Model Support**
* **Qwen3-Next**: Added support for Qwen3-Next-80B-A3B-Instruct with full graph mode, MTP, quantization, and NZ optimization (#3450, #3572, #3428, #3918, #4058, #4245, #4070, #4477)
* **DeepSeek-R1 & DeepSeek-V3.2-Exp**: Added support for DeepSeek-R1 multimodal capabilities and DeepSeek-V3.2-Exp with MTP support (#3631, #3900, #3908, #4191)
* **InternVL**: Added support for InternVL models with e2e tests and accuracy evaluation (#3796, #3964)
* **Kimi-K2**: Fixed weight loading for Kimi-K2 model (#3798)

**Core Features**
* **Context Parallel & Sequence Parallel (CP/SP)**: Added support for context parallel (PCP) and data context parallel (DCP) with ACLGraph, MTP, and chunked prefill (#3260, #3731, #3801, #4066, #4098, #4183)
* **Full Graph Mode (ACLGraph)**: Enhanced full graph mode with GQA support, memory optimizations, and unified logic between ACLGraph and Torchair (#3560, #3970, #3812, #3879, #3888, #3894)
* **Multi-Token Prediction (MTP)**: Improved MTP support with chunked prefill, quantization, full graph mode, and PCP/DCP integration (#2711, #2713, #3620, #3845, #3910, #3915, #4102, #4111)
* **PD Disaggregation**: Set ADXL engine as default backend for disaggregated prefill with improved documentation and feature guides (#3761, #3950, #4012)
* **KV Pool & Mooncake**: Enhanced KV pool with developer guide and Mooncake connector support for PCP/DCP with multiple input suffixes (#3690, #3752, #3849, #4183)
* **Full Decode Only Mode**: Added support for Qwen3-Next in full_decode_only mode with bug fixes for rare edge cases (#3949, #3986)

**Developer Documentation**
* Added comprehensive developer guides for ACLGraph, MTP, KV Pool, EPLB, and PD disaggregation features (#3683, #3770, #3752, #3759, #3950)

### Features

* **Sampling & Decoding**: Added support for min_p sampling parameter with performance enhancements (#4529)
* **Quantization**: Enhanced quantization support with inductor fusion and dynamic quantization fusion pass (#4168)
* **Prefix Caching**: Improved performance of prefix cache features (#4022)

### Hardware and Operator Support

* **Operator Fusion**: Added fused matmul/reduce-scatter kernel, mrope fusion op, and npu_fused_infer_attention_score support (#3693, #3708, #4025)
* **Custom Operators**: Added Triton chunk_gated_delta_rule ops for Qwen3-Next (#4070)
* **MLA/SFA**: Refactored SFA into MLA architecture (#3769)
* **Chip Optimization**: Optimized chip type judgement code and added machine-specific fusion op handling (#4485, #4270)

### Performance

* **Async Scheduling**: Improved async scheduling with async copy fixes and eliminated HD synchronization for DeepSeek-V3.2 (#4113, #4233, #4805)
* **FlashComm**: Enhanced FlashComm v2 optimization with o_shared linear and communication domain fixes (#3232, #4188, #4458)
* **Memory Optimization**: Optimized memory usage for DeepSeek MTP and removed redundant D2H operations (#2713, #4063)
* **MoE Optimization**: Optimized all2allv for MoE models (#3738)
* **Attention Optimization**: Moved attention update stream out of loop and converted BSND to TND format for long sequence optimization (#3848, #3778)
* **Quantization Performance**: Moved quantization before allgather in Allgather EP (#3420)
* **Model Runner**: Deleted redundant operations in model_runner and forward_context (#3677)
* **Layerwise Connector**: Performance optimization for layerwise connector (#4043)
* **Vision Models**: Removed Qwen2.5-VL modeling files and added patch for VisionAttention performance (#4349)
* **Sampling**: Removed VLLM_ASCEND_ENABLE_TOPK_TOPP_OPTIMIZATION flag (#4860)

### Dependencies

* **torch-npu**: Updated to version 2.7.1 with bug fixes for npu_mm_reduce_scatter_base when sp size >= 16 (#3896, #4433, #6167)
* **vLLM**: Upgraded to vLLM 0.11.2 (#4400)
* **Build Dependencies**: Fixed buildwheel dependency installation (#6211)

### Deprecation & Breaking Changes

* **Qwen3-Next Model Files**: Removed Qwen3-Next model files (now using upstream implementation) (#4573)
* **Qwen2.5-VL Modeling**: Removed Qwen2.5-VL modeling files in favor of patch-based approach (#4349)

### Documentation

* **Model Tutorials**: Added and refactored tutorials for DeepSeek-V3.2-Exp with simplified MLAPO installation steps (#3871, #4024)
* **Feature Guides**: Added comprehensive guides for disaggregated-prefill, ACLGraph, MTP, KV Pool, and EPLB (#3950, #3683, #3770, #3752, #3759)
* **KV Pool**: Added ADXL timeout parameter documentation in KV pool user guide (#4012)

### Others

* **Error Handling**: Added error log for VL models when enabling FLASHCOMM (#4272)
* **Bug Fixes**: Fixed various bugs including MOE fusion operator usage, prefix cache performance, and async scheduling hangs (#3834, #4022, #4233)
* **Testing**: Enhanced nightly CI optimization and added comprehensive test coverage for new features (#3858, #3898, #4509, #4798, #4886)
