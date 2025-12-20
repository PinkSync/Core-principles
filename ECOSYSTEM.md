# PinkSync Ecosystem - Source Repositories

## Primary Source Repository

**Repository:** [github.com/pinkycollie/pinksync](https://github.com/pinkycollie/pinksync)

This repository contains all the branches with features, tools, and microservices that compose the full PinkSync ecosystem.

## Branch Structure

The source repository contains multiple branches, each representing a different feature, tool, or microservice:

### Feature Branches
- Each branch contains a specific accessibility feature or capability
- Features are designed to be modular and composable
- Follow the PinkSync contract specifications

### Tools Branches
- Specialized tools for accessibility testing, validation, and monitoring
- Command-line utilities and helper scripts
- Integration tools for third-party services

### Microservices Branches
- Individual microservices that extend PinkSync functionality
- Each microservice follows the broker pattern
- Can be deployed independently or as part of the ecosystem

## Integration with Core-principles

This repository (PinkSync/Core-principles) defines:
- ✅ Core specifications and contracts (`/specs`)
- ✅ Broker API reference implementation (`/api`)
- ✅ Core principles and philosophy (`Core.md`, `README.md`)

The source repository (pinkycollie/pinksync) contains:
- 🔧 Feature implementations
- 🛠️ Tools and utilities
- 🎯 Microservices
- 🧪 Experimental features

## How to Discover Available Features

### List All Branches

```bash
# Clone the source repository
git clone https://github.com/pinkycollie/pinksync
cd pinksync

# List all branches (features, tools, microservices)
git branch -r
```

### Explore a Specific Feature

```bash
# Check out a feature branch
git checkout feature/sign-language-interpreter

# Review the feature documentation
cat README.md
```

### Integrate a Feature

Each branch in the source repository should contain:
1. `README.md` - Feature description and usage
2. `package.json` or `requirements.txt` - Dependencies
3. `docker-compose.yml` - Deployment configuration (if applicable)
4. Integration instructions

## API Endpoint Discovery

The PinkSync broker provides an endpoint to discover available features from the ecosystem:

```bash
GET /api/ecosystem/features
```

This endpoint can query the source repository and list available branches/features.

## Contributing Features

To contribute a new feature to the ecosystem:

1. Fork [github.com/pinkycollie/pinksync](https://github.com/pinkycollie/pinksync)
2. Create a feature branch: `git checkout -b feature/my-accessibility-tool`
3. Implement your feature following PinkSync contracts
4. Add documentation and tests
5. Submit a pull request

## Architecture

```
PinkSync Ecosystem
├── PinkSync/Core-principles (this repo)
│   ├── /specs (contracts - source of truth)
│   ├── /api (broker reference implementation)
│   └── Documentation
│
└── pinkycollie/pinksync (source repo)
    ├── feature/sign-language-interpreter
    ├── feature/visual-alerts
    ├── tool/accessibility-validator
    ├── tool/compliance-checker
    ├── microservice/caption-generator
    ├── microservice/asl-video-processor
    └── ... (many more branches)
```

## Deployment Strategy

### Option 1: Monorepo Deployment
Deploy all features from a single repository:
```bash
git clone --recurse-submodules https://github.com/pinkycollie/pinksync
docker-compose up
```

### Option 2: Selective Deployment
Deploy only specific features:
```bash
git clone https://github.com/pinkycollie/pinksync
git checkout feature/sign-language-interpreter
docker-compose -f docker-compose.feature.yml up
```

### Option 3: Microservices Deployment
Deploy each microservice independently:
```bash
# Deploy caption generator
git clone -b microservice/caption-generator https://github.com/pinkycollie/pinksync caption-gen
cd caption-gen && docker-compose up

# Deploy ASL processor
git clone -b microservice/asl-video-processor https://github.com/pinkycollie/pinksync asl-proc
cd asl-proc && docker-compose up
```

## Contract Compliance

All features, tools, and microservices in the source repository MUST:
- ✅ Follow the contracts defined in `/specs` of this repository
- ✅ Emit events to the PinkSync broker
- ✅ Respect compliance levels
- ✅ Support deaf-first accessibility principles

## Support

For questions about:
- **Specifications and Contracts**: Open issues in PinkSync/Core-principles
- **Feature Implementation**: Open issues in pinkycollie/pinksync
- **Integration Help**: Check documentation in each feature branch

## Links

- **Specifications Repository**: https://github.com/PinkSync/Core-principles
- **Source Repository**: https://github.com/pinkycollie/pinksync
- **Documentation**: https://docs.pinksync.org (coming soon)
- **Community**: https://community.pinksync.org (coming soon)

---

*The power of PinkSync comes from its ecosystem of features, tools, and microservices all working together through a unified contract.*
